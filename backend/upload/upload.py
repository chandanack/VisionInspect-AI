from fastapi import APIRouter, UploadFile, File, Form

from backend.preprocess import (
    preprocess_image,
    analyze_image_quality
)

from backend.feature_extractor import extract_features
from backend.anomaly_detector import predict_anomaly
from backend.inspection_history import add_inspection

import torch
from datetime import datetime
import uuid


router = APIRouter()


# ==========================================
# Load Normal Feature Database
# ==========================================

normal_features = torch.load(
    "normal_features.pt",
    weights_only=False
)


# ==========================================
# MVTec AD Categories
# ==========================================

CATEGORIES = [
    "bottle",
    "cable",
    "capsule",
    "carpet",
    "grid",
    "hazelnut",
    "leather",
    "metal_nut",
    "pill",
    "screw",
    "tile",
    "toothbrush",
    "transistor",
    "wood",
    "zipper"
]


# ==========================================
# Category-Specific Thresholds
# ==========================================

THRESHOLDS = {
    "bottle": 1.1508,
    "cable": 1.8222,
    "capsule": 0.9139,
    "carpet": 0.6511,
    "grid": 1.0459,
    "hazelnut": 2.3201,
    "leather": 0.7306,
    "metal_nut": 1.8214,
    "pill": 1.0704,
    "screw": 1.6943,
    "tile": 1.2502,
    "toothbrush": 1.6475,
    "transistor": 1.7346,
    "wood": 1.3598,
    "zipper": 1.4081
}


# ==========================================
# Inspection Endpoint
# ==========================================

@router.post("/upload")
async def upload_image(
    category: str = Form(...),
    file: UploadFile = File(...)
):

    # ======================================
    # Validate Category
    # ======================================

    if category not in CATEGORIES:

        return {
            "message": "Invalid category",
            "available_categories": CATEGORIES
        }


    # ======================================
    # Get Category Normal Features
    # ======================================

    category_features = normal_features.get(
        category
    )

    if category_features is None:

        return {
            "message": (
                "Normal features not found "
                "for this category"
            ),
            "category": category
        }


    # ======================================
    # Get Category Threshold
    # ======================================

    threshold = THRESHOLDS.get(
        category
    )

    if threshold is None:

        return {
            "message": (
                "Threshold not configured "
                "for this category"
            ),
            "category": category
        }


    # ======================================
    # Read Image
    # ======================================

    image_bytes = await file.read()


    # ======================================
    # Image Quality Analysis
    # ======================================

    quality_report = analyze_image_quality(
        image_bytes
    )


    # ======================================
    # Image Preprocessing
    # ======================================

    image = preprocess_image(
        image_bytes
    )


    # ======================================
    # Feature Extraction
    # ======================================

    features = extract_features(
        image
    )


    # ======================================
    # Anomaly Detection
    # ======================================

    result = predict_anomaly(
        features,
        category_features,
        threshold=threshold
    )


    # ======================================
    # Generate Inspection ID
    # ======================================

    inspection_id = (
        "INS-"
        + uuid.uuid4().hex[:8].upper()
    )


    # ======================================
    # Inspection Timestamp
    # ======================================

    inspection_time = (
        datetime.now().isoformat()
    )


    # ======================================
    # Determine Product Status
    # ======================================

    if result["result"] == "DEFECT":

        product_status = "REJECT"

    else:

        product_status = "ACCEPT"


    # ======================================
    # Build Inspection Report
    # ======================================

    inspection_report = {

        "inspection_id": inspection_id,

        "inspection_time": inspection_time,

        "filename": file.filename,

        "category": category,

        "prediction": result["result"],

        "product_status": product_status,

        "anomaly_score": result[
            "anomaly_score"
        ],

        "threshold": result[
            "threshold"
        ],

        "decision": result[
            "decision"
        ],

        "image_shape": list(
            image.shape
        ),

        "feature_shape": list(
            features.shape
        ),

        "quality_report": quality_report
    }


    # ======================================
    # Store Inspection
    # ======================================

    add_inspection(
        inspection_report
    )


    # ======================================
    # Final API Response
    # ======================================

    return {

        "message": (
            "Inspection completed successfully"
        ),

        "inspection_report": (
            inspection_report
        )
    }
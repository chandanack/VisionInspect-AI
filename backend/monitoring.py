from fastapi import APIRouter

from backend.inspection_history import (
    get_inspections,
    get_statistics
)


router = APIRouter()


# ==========================================
# Get All Inspection Reports
# ==========================================

@router.get("/inspections")
def inspections():

    return {
        "message": "Inspection history retrieved successfully",
        "inspections": get_inspections()
    }


# ==========================================
# Get Inspection Statistics
# ==========================================

@router.get("/inspection-statistics")
def inspection_statistics():

    return {
        "message": "Inspection statistics retrieved successfully",
        "statistics": get_statistics()
    }
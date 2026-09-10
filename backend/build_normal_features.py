import os
import torch

from backend.preprocess import preprocess_image
from backend.feature_extractor import extract_features


# MVTec dataset location
DATASET_PATH = r"C:\Users\chand\Downloads\mvtec_anomaly_detection"


# All MVTec categories
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


# Store normal features for every category
all_normal_features = {}


for category in CATEGORIES:

    print(f"\nProcessing category: {category}")

    good_path = os.path.join(
        DATASET_PATH,
        category,
        "train",
        "good"
    )

    features = []

    if not os.path.exists(good_path):
        print(f"WARNING: Path not found: {good_path}")
        continue

    for filename in os.listdir(good_path):

        if filename.lower().endswith(
            (".png", ".jpg", ".jpeg")
        ):

            image_path = os.path.join(
                good_path,
                filename
            )

            with open(image_path, "rb") as f:
                image_bytes = f.read()

            # Preprocess image
            image = preprocess_image(image_bytes)

            # Extract ResNet18 features
            feature = extract_features(image)

            features.append(feature)

    if features:

        # Combine all features for this category
        normal_features = torch.cat(
            features,
            dim=0
        )

        all_normal_features[category] = normal_features

        print(
            f"{category}: "
            f"{len(features)} normal images → "
            f"{normal_features.shape}"
        )

    else:

        print(
            f"No normal images found for {category}"
        )


# Save all category feature databases
torch.save(
    all_normal_features,
    "normal_features.pt"
)


print("\n===================================")
print("Normal feature database created!")
print("===================================")

print(
    "Categories:",
    list(all_normal_features.keys())
)

print(
    "Total categories:",
    len(all_normal_features)
)
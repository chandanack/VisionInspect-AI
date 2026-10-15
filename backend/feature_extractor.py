
import timm
import torch
import threading


# ==========================================
# Lazy Load Pretrained ResNet18
# ==========================================

_model = None
_model_lock = threading.Lock()


def get_model():
    """
    Load ResNet18 only when feature extraction
    is first requested.
    """
    global _model

    if _model is None:
        with _model_lock:
            if _model is None:
                _model = timm.create_model(
                    "resnet18",
                    pretrained=True,
                    num_classes=0,
                )
                _model.eval()

    return _model


# ==========================================
# ImageNet Normalization Values
# ==========================================

MEAN = torch.tensor(
    [0.485, 0.456, 0.406]
).view(1, 3, 1, 1)

STD = torch.tensor(
    [0.229, 0.224, 0.225]
).view(1, 3, 1, 1)


# ==========================================
# Feature Extraction
# ==========================================

def extract_features(image):
    # Convert NumPy image to PyTorch tensor
    tensor = torch.as_tensor(
        image,
        dtype=torch.float32,
    )

    # HWC -> CHW
    tensor = tensor.permute(2, 0, 1)

    # Add batch dimension
    tensor = tensor.unsqueeze(0)

    # Apply ImageNet normalization
    tensor = (tensor - MEAN) / STD

    # Load model only when needed
    model = get_model()

    # Extract ResNet18 features
    with torch.inference_mode():
        features = model(tensor)

    return features


print("Feature extractor ready")

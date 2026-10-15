
import joblib
import numpy as np
import threading


CLASSIFIER_PATH = "backend/defect_classifier.pkl"

_classifier = None
_classifier_lock = threading.Lock()


def load_defect_classifier():
    """Load the classifier once and reuse it."""
    global _classifier

    if _classifier is None:
        with _classifier_lock:
            if _classifier is None:
                _classifier = joblib.load(
                    CLASSIFIER_PATH
                )

    return _classifier


def predict_defect(features):
    classifier = load_defect_classifier()

    features = np.asarray(features)

    if features.ndim == 1:
        features = features.reshape(1, -1)

    prediction = classifier.predict(features)[0]

    return prediction

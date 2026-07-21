"""
Loads the trained model and provides predict() used by the scanner blueprint.
"""
import joblib
import numpy as np
import os
from app.ml.feature_extractor import extract_features, features_to_vector

MODEL_PATH = os.path.join(os.path.dirname(__file__), 'model.joblib')
_cache = {}


def _load_model():
    if 'bundle' not in _cache:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(
                "Model not found. Run: python -m app.ml.train_model"
            )
        _cache['bundle'] = joblib.load(MODEL_PATH)
    return _cache['bundle']


def predict(url: str) -> dict:
    """
    Extracts features from url, runs ML model, returns prediction dict:
    {
        prediction: str,   # Safe / Suspicious / Phishing
        confidence: float, # 0.0–1.0
        risk_score: int,   # 0–100
        features: dict
    }
    """
    bundle = _load_model()
    clf = bundle['model']
    le = bundle['label_encoder']

    features = extract_features(url)
    vector = np.array(features_to_vector(features)).reshape(1, -1)

    proba = clf.predict_proba(vector)[0]
    pred_idx = int(np.argmax(proba))
    prediction = le.inverse_transform([pred_idx])[0]
    confidence = float(proba[pred_idx])

    # Risk score: weighted combination of phishing & suspicious probabilities
    classes = list(le.classes_)
    phishing_prob = proba[classes.index('Phishing')] if 'Phishing' in classes else 0
    suspicious_prob = proba[classes.index('Suspicious')] if 'Suspicious' in classes else 0
    risk_score = int(round((phishing_prob * 100 * 0.8) + (suspicious_prob * 100 * 0.4)))
    risk_score = max(0, min(100, risk_score))

    return {
        'prediction': prediction,
        'confidence': round(confidence * 100, 2),
        'risk_score': risk_score,
        'features': features,
    }

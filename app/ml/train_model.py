"""
Train a Random Forest classifier on synthetic phishing/safe/suspicious URL features.
Run once: python -m app.ml.train_model
"""
import numpy as np
import joblib
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.preprocessing import LabelEncoder

FEATURE_COUNT = 15
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'model.joblib')

def generate_synthetic_data(n=3000):
    rng = np.random.default_rng(42)
    X, y = [], []

    # Safe websites (~40%)
    for _ in range(int(n * 0.4)):
        X.append([
            rng.integers(15, 60),    # url_length
            1,                        # has_https
            0,                        # has_ip
            rng.integers(0, 2),      # subdomain_count
            rng.integers(0, 2),      # special_char_count
            rng.integers(0, 2),      # suspicious_keywords
            rng.integers(1, 4),      # dot_count
            0,                        # has_at_symbol
            rng.integers(365, 5000), # domain_age_days
            1,                        # ssl_valid
            0,                        # has_login_form
            rng.integers(0, 10),     # external_links
            0,                        # hidden_elements
            0,                        # redirect_count
            0,                        # has_suspicious_js
        ])
        y.append('Safe')

    # Suspicious websites (~30%)
    for _ in range(int(n * 0.3)):
        X.append([
            rng.integers(60, 100),
            rng.integers(0, 2),
            0,
            rng.integers(1, 3),
            rng.integers(2, 5),
            rng.integers(2, 5),
            rng.integers(3, 7),
            0,
            rng.integers(30, 365),
            rng.integers(0, 2),
            rng.integers(0, 2),
            rng.integers(10, 30),
            rng.integers(0, 3),
            rng.integers(0, 2),
            rng.integers(0, 2),
        ])
        y.append('Suspicious')

    # Phishing websites (~30%)
    for _ in range(int(n * 0.3)):
        X.append([
            rng.integers(80, 200),
            0,
            rng.integers(0, 2),
            rng.integers(2, 5),
            rng.integers(4, 10),
            rng.integers(4, 10),
            rng.integers(5, 12),
            rng.integers(0, 2),
            rng.integers(-1, 60),
            0,
            1,
            rng.integers(20, 60),
            rng.integers(2, 8),
            rng.integers(1, 5),
            1,
        ])
        y.append('Phishing')

    return np.array(X, dtype=float), np.array(y)


def train():
    print("Generating training data...")
    X, y = generate_synthetic_data(3000)

    le = LabelEncoder()
    y_enc = le.fit_transform(y)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y_enc, test_size=0.2, random_state=42, stratify=y_enc
    )

    clf = RandomForestClassifier(n_estimators=200, max_depth=12, random_state=42, n_jobs=-1)
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)
    print(classification_report(y_test, y_pred, target_names=le.classes_))

    joblib.dump({'model': clf, 'label_encoder': le}, MODEL_PATH)
    print(f"Model saved to {MODEL_PATH}")


if __name__ == '__main__':
    train()

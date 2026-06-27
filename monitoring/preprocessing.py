"""
Feature extraction and normalization utilities for sensor readings.

The scaler is fitted once (via import_banner) and reused for every
subsequent reading. Raw features are always stored first; normalization
is applied before similarity search or model inference.
"""

import numpy as np
import joblib
from pathlib import Path

from django.conf import settings

from .models import FEATURE_COLUMNS


def extract_features(metrics: dict) -> list:
    """Extract ordered feature values from a raw metrics dict.

    Missing or non-numeric columns default to 0.0.
    """
    return [float(metrics.get(col) or 0.0) for col in FEATURE_COLUMNS]


def fit_and_save_scaler(feature_matrix: np.ndarray):
    """Fit a StandardScaler on *feature_matrix* and persist it to disk.

    Returns the fitted scaler instance.
    """
    from sklearn.preprocessing import StandardScaler

    scaler = StandardScaler()
    scaler.fit(feature_matrix)

    path = Path(settings.SCALER_PATH)
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(scaler, path)
    return scaler


def load_scaler():
    """Load the persisted StandardScaler, or return None if not yet fitted."""
    path = Path(settings.SCALER_PATH)
    if not path.exists():
        return None
    return joblib.load(path)


def normalize_features(raw_features: list) -> list:
    """Normalize raw features using the fitted scaler.

    If the scaler has not been fitted yet, raw features are returned
    unchanged (safe fallback during initial setup).
    """
    scaler = load_scaler()
    if scaler is None:
        return raw_features
    arr = np.array(raw_features, dtype=float).reshape(1, -1)
    return scaler.transform(arr)[0].tolist()

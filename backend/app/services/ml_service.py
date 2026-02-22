import os
import joblib
import numpy as np
from pathlib import Path

MODEL_DIR = Path(__file__).parent.parent.parent / "ml" / "saved_models"

_cache: dict = {}

def _load(task: str, model_name: str):
    key = f"{task}_{model_name}"
    if key not in _cache:
        path = MODEL_DIR / f"{key}.pkl"
        if not path.exists():
            raise FileNotFoundError(f"Model not found: {path}")
        _cache[key] = joblib.load(path)
    return _cache[key]

def predict(task: str, model_name: str, features: dict) -> dict:
    pipeline = _load(task, model_name)
    from ml.preprocessor import FEATURE_COLS, ENCODING
    # Encode categorical values the same way as training
    encoded = {}
    for col, val in features.items():
        if col in ENCODING:
            encoded[col] = ENCODING[col].get(str(val), 0)
        else:
            encoded[col] = val
    X = [[encoded.get(col, 0) for col in FEATURE_COLS]]

    result = float(pipeline.predict(X)[0])
    probability = None
    if task == "risk" and hasattr(pipeline, "predict_proba"):
        proba = pipeline.predict_proba(X)[0]
        probability = float(proba[1])

    importance = {}
    try:
        clf = pipeline.named_steps.get("clf") or pipeline.steps[-1][1]
        if hasattr(clf, "feature_importances_"):
            imp = clf.feature_importances_
            importance = {col: round(float(v), 4) for col, v in zip(FEATURE_COLS, imp)}
        elif hasattr(clf, "coef_"):
            coef = np.abs(clf.coef_).flatten() if clf.coef_.ndim > 1 else np.abs(clf.coef_)
            importance = {col: round(float(v), 4) for col, v in zip(FEATURE_COLS, coef)}
    except Exception:
        pass

    return {"result": result, "probability": probability, "feature_importance": importance}

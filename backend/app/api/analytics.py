from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models.user import User
from app.models.student import Student
from app.models.prediction import ModelMetric
from app.schemas.prediction import ModelMetricOut
from app.services.auth_service import get_current_user

router = APIRouter()

@router.get("/overview")
def overview(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    total = db.query(func.count(Student.id)).scalar()
    avg_g1 = db.query(func.avg(Student.g1)).scalar()
    avg_g2 = db.query(func.avg(Student.g2)).scalar()
    high_risk = db.query(func.count(Student.id)).filter(Student.g2 < 10).scalar()
    return {
        "total_students": total,
        "avg_g1": round(avg_g1 or 0, 2),
        "avg_g2": round(avg_g2 or 0, 2),
        "high_risk_count": high_risk,
    }

@router.get("/distribution")
def distribution(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    rows = db.query(Student.g2).all()
    buckets = {"0-9": 0, "10-12": 0, "13-15": 0, "16-18": 0, "19-20": 0}
    for (g,) in rows:
        if g is None:
            continue
        if g <= 9:
            buckets["0-9"] += 1
        elif g <= 12:
            buckets["10-12"] += 1
        elif g <= 15:
            buckets["13-15"] += 1
        elif g <= 18:
            buckets["16-18"] += 1
        else:
            buckets["19-20"] += 1
    return buckets

@router.get("/model-comparison", response_model=list[ModelMetricOut])
def model_comparison(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return db.query(ModelMetric).order_by(ModelMetric.task, ModelMetric.model_name).all()

@router.get("/feature-importance")
def feature_importance(
    task: str = "grade",
    model_name: str = "random_forest",
    _: User = Depends(get_current_user),
):
    import joblib, numpy as np
    from pathlib import Path
    from ml.preprocessor import FEATURE_COLS
    model_path = Path(__file__).parent.parent.parent / "ml" / "saved_models" / f"{task}_{model_name}.pkl"
    if not model_path.exists():
        return {}
    pipeline = joblib.load(model_path)
    try:
        clf = pipeline.named_steps.get("clf") or pipeline.steps[-1][1]
        if hasattr(clf, "feature_importances_"):
            imp = clf.feature_importances_
            return {col: round(float(v), 4) for col, v in zip(FEATURE_COLS, imp)}
        elif hasattr(clf, "coef_"):
            coef = np.abs(clf.coef_).flatten() if clf.coef_.ndim > 1 else np.abs(clf.coef_)
            return {col: round(float(v), 4) for col, v in zip(FEATURE_COLS, coef)}
    except Exception:
        pass
    return {}

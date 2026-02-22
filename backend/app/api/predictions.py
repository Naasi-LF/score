from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
import pandas as pd
import io
from app.database import get_db
from app.models.user import User
from app.models.prediction import Prediction
from app.schemas.prediction import PredictRequest, PredictResult, PredictionRecord
from app.services.auth_service import get_current_user
from app.services import ml_service

router = APIRouter()

@router.post("/single", response_model=PredictResult)
def predict_single(
    req: PredictRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        out = ml_service.predict(req.task, req.model_name, req.features)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    record = Prediction(
        student_id=req.student_id,
        input_data=req.features,
        task=req.task,
        model_name=req.model_name,
        result=out["result"],
        probability=out.get("probability"),
        created_by=current_user.id,
    )
    db.add(record)
    db.commit()

    return PredictResult(
        task=req.task,
        model_name=req.model_name,
        result=out["result"],
        probability=out.get("probability"),
        feature_importance=out.get("feature_importance"),
    )

@router.post("/batch")
async def predict_batch(
    task: str,
    model_name: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    content = await file.read()
    try:
        df = pd.read_csv(io.BytesIO(content)) if file.filename.endswith(".csv") else pd.read_excel(io.BytesIO(content))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Cannot parse file: {e}")

    df.columns = df.columns.str.lower()
    results = []
    for _, row in df.iterrows():
        features = row.to_dict()
        try:
            out = ml_service.predict(task, model_name, features)
            results.append({**features, "prediction": out["result"], "probability": out.get("probability")})
            db.add(Prediction(
                input_data=features, task=task, model_name=model_name,
                result=out["result"], probability=out.get("probability"),
                created_by=current_user.id,
            ))
        except Exception as e:
            results.append({**features, "prediction": None, "error": str(e)})
    db.commit()
    return {"count": len(results), "results": results}

@router.get("/history", response_model=list[PredictionRecord])
def prediction_history(
    task: str = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    q = db.query(Prediction)
    if task:
        q = q.filter(Prediction.task == task)
    return q.order_by(Prediction.created_at.desc()).offset(skip).limit(limit).all()

from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Any

class PredictRequest(BaseModel):
    task: str           # grade / risk
    model_name: str
    features: dict[str, Any]
    student_id: Optional[int] = None

class PredictResult(BaseModel):
    task: str
    model_name: str
    result: float
    probability: Optional[float] = None
    feature_importance: Optional[dict[str, float]] = None

class PredictionRecord(BaseModel):
    id: int
    student_id: Optional[int]
    task: str
    model_name: str
    result: float
    probability: Optional[float]
    created_at: datetime

    class Config:
        from_attributes = True

class ModelMetricOut(BaseModel):
    task: str
    model_name: str
    mae: Optional[float] = None
    rmse: Optional[float] = None
    r2: Optional[float] = None
    accuracy: Optional[float] = None
    precision: Optional[float] = None
    recall: Optional[float] = None
    f1: Optional[float] = None
    roc_auc: Optional[float] = None
    trained_at: datetime

    class Config:
        from_attributes = True

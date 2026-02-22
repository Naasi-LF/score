from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, func, ForeignKey
from app.database import Base

class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="SET NULL"), nullable=True)
    input_data = Column(JSON, nullable=False)
    task = Column(String, nullable=False)        # grade / risk
    model_name = Column(String, nullable=False)
    result = Column(Float)
    probability = Column(Float, nullable=True)   # risk probability
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ModelMetric(Base):
    __tablename__ = "model_metrics"

    id = Column(Integer, primary_key=True, index=True)
    task = Column(String, nullable=False)
    model_name = Column(String, nullable=False)
    # regression
    mae = Column(Float, nullable=True)
    rmse = Column(Float, nullable=True)
    r2 = Column(Float, nullable=True)
    # classification
    accuracy = Column(Float, nullable=True)
    precision = Column(Float, nullable=True)
    recall = Column(Float, nullable=True)
    f1 = Column(Float, nullable=True)
    roc_auc = Column(Float, nullable=True)
    trained_at = Column(DateTime(timezone=True), server_default=func.now())

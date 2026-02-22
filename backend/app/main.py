from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.models import User, Student, Prediction, ModelMetric
from app.api import auth, students, predictions, analytics
from app.services.auth_service import hash_password
from sqlalchemy.orm import Session

app = FastAPI(title="Student Score Analysis System", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(students.router, prefix="/api/students", tags=["students"])
app.include_router(predictions.router, prefix="/api/predictions", tags=["predictions"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    # Seed default admin user
    db = Session(engine)
    try:
        if not db.query(User).filter(User.username == "admin").first():
            db.add(User(username="admin", hashed_password=hash_password("admin123")))
            db.commit()
    finally:
        db.close()

@app.get("/health")
def health():
    return {"status": "ok"}

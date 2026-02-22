from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session
import pandas as pd
import io
from app.database import get_db
from app.models.user import User
from app.schemas.student import StudentCreate, StudentOut, StudentPage
from app.services.student_service import get_students, create_student, delete_student, bulk_create_students
from app.services.auth_service import get_current_user

router = APIRouter()

@router.get("", response_model=StudentPage)
def list_students(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    total, items = get_students(db, skip, limit)
    return {"total": total, "items": items}

@router.post("", response_model=StudentOut)
def add_student(
    data: StudentCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return create_student(db, data)

@router.delete("/{student_id}")
def remove_student(
    student_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    if not delete_student(db, student_id):
        raise HTTPException(status_code=404, detail="Student not found")
    return {"ok": True}

@router.post("/import")
async def import_students(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    content = await file.read()
    try:
        if file.filename.endswith(".csv"):
            df = pd.read_csv(io.BytesIO(content))
        else:
            df = pd.read_excel(io.BytesIO(content))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Cannot parse file: {e}")

    required = {"name", "age", "sex", "address", "famsize", "medu", "fedu",
                "studytime", "failures", "absences", "activities", "g1", "g2"}
    missing = required - set(df.columns.str.lower())
    if missing:
        raise HTTPException(status_code=400, detail=f"Missing columns: {missing}")

    df.columns = df.columns.str.lower()
    records = df[list(required)].to_dict(orient="records")
    count = bulk_create_students(db, records)
    return {"imported": count}

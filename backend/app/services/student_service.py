from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.student import Student
from app.schemas.student import StudentCreate

def get_students(db: Session, skip: int = 0, limit: int = 20):
    total = db.query(func.count(Student.id)).scalar()
    items = db.query(Student).offset(skip).limit(limit).all()
    return total, items

def create_student(db: Session, data: StudentCreate) -> Student:
    student = Student(**data.model_dump())
    db.add(student)
    db.commit()
    db.refresh(student)
    return student

def delete_student(db: Session, student_id: int) -> bool:
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        return False
    db.delete(student)
    db.commit()
    return True

def bulk_create_students(db: Session, records: list[dict]) -> int:
    students = [Student(**r) for r in records]
    db.bulk_save_objects(students)
    db.commit()
    return len(students)

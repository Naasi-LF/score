from sqlalchemy import Column, Integer, String, DateTime, func
from app.database import Base

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    student_no = Column(String, unique=True, nullable=True, index=True)
    name = Column(String, nullable=False)
    age = Column(Integer)
    sex = Column(String(1))          # M / F
    address = Column(String(1))      # U / R
    famsize = Column(String(3))      # LE3 / GT3
    medu = Column(Integer)           # 0-4
    fedu = Column(Integer)           # 0-4
    studytime = Column(Integer)      # 1-4
    failures = Column(Integer)       # 0-4
    absences = Column(Integer)
    activities = Column(String(3))   # yes / no
    g1 = Column(Integer)
    g2 = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

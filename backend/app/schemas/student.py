from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class StudentBase(BaseModel):
    name: str
    age: int
    sex: str
    address: str
    famsize: str
    medu: int
    fedu: int
    studytime: int
    failures: int
    absences: int
    activities: str
    g1: int
    g2: int

class StudentCreate(StudentBase):
    pass

class StudentOut(StudentBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class StudentPage(BaseModel):
    total: int
    items: list[StudentOut]

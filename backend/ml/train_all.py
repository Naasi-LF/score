#!/usr/bin/env python
"""One-shot training script. Run inside the backend container:
   docker compose exec backend python ml/train_all.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pathlib import Path
from ml.trainer import train_all
from app.database import SessionLocal

CSV = Path(__file__).parent / "datasets" / "student-mat.csv"
if not CSV.exists():
    print(f"ERROR: dataset not found at {CSV}")
    sys.exit(1)

db = SessionLocal()
try:
    results = train_all(str(CSV), db_session=db)
    print(f"\nDone. Trained {len(results)} models.")
finally:
    db.close()

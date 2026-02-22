import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder

# All input features used for training/inference
FEATURE_COLS = [
    "age", "medu", "fedu", "studytime", "failures", "absences",
    "g1", "g2",
    "sex", "address", "famsize", "activities",
]

CATEGORICAL_COLS = ["sex", "address", "famsize", "activities"]
NUMERIC_COLS = [c for c in FEATURE_COLS if c not in CATEGORICAL_COLS]

# Fixed encoding maps so train/inference are consistent
ENCODING = {
    "sex":        {"M": 0, "F": 1},
    "address":    {"U": 0, "R": 1},
    "famsize":    {"LE3": 0, "GT3": 1},
    "activities": {"no": 0, "yes": 1},
}

def encode_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for col, mapping in ENCODING.items():
        if col in df.columns:
            df[col] = df[col].map(mapping).fillna(0).astype(int)
    return df

def prepare_dataset(csv_path: str):
    df = pd.read_csv(csv_path, sep=";")
    df.columns = df.columns.str.lower()

    # Rename to match our schema
    rename = {"medu": "medu", "fedu": "fedu", "studytime": "studytime",
               "failures": "failures", "absences": "absences",
               "activities": "activities", "g1": "g1", "g2": "g2", "g3": "g3"}
    df = df.rename(columns=rename)

    df = encode_features(df)

    X = df[FEATURE_COLS].fillna(0)
    y_grade = df["g3"].astype(float)
    y_risk = (df["g3"] < 10).astype(int)

    return X, y_grade, y_risk

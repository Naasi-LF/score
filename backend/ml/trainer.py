import joblib
from pathlib import Path
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.svm import SVC, SVR
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.model_selection import train_test_split

from ml.preprocessor import prepare_dataset
from ml.evaluator import evaluate_regression, evaluate_classification

MODELS_DIR = Path(__file__).parent / "saved_models"
MODELS_DIR.mkdir(exist_ok=True)

GRADE_MODELS = {
    "random_forest": RandomForestRegressor(n_estimators=100, random_state=42),
    "svm":           SVR(kernel="rbf", C=10, gamma="scale"),
    "decision_tree": DecisionTreeRegressor(max_depth=8, random_state=42),
    "linear":        LinearRegression(),
}

RISK_MODELS = {
    "random_forest":    RandomForestClassifier(n_estimators=100, random_state=42),
    "svm":              SVC(kernel="rbf", C=10, gamma="scale", probability=True),
    "decision_tree":    DecisionTreeClassifier(max_depth=8, random_state=42),
    "logistic":         LogisticRegression(max_iter=1000, random_state=42),
}

def train_all(csv_path: str, db_session=None):
    X, y_grade, y_risk = prepare_dataset(csv_path)
    X_tr_g, X_te_g, y_tr_g, y_te_g = train_test_split(X, y_grade, test_size=0.2, random_state=42)
    X_tr_r, X_te_r, y_tr_r, y_te_r = train_test_split(X, y_risk,  test_size=0.2, random_state=42)

    results = []

    for name, model in GRADE_MODELS.items():
        pipe = Pipeline([("scaler", StandardScaler()), ("clf", model)])
        pipe.fit(X_tr_g, y_tr_g)
        metrics = evaluate_regression(pipe, X_te_g, y_te_g)
        joblib.dump(pipe, MODELS_DIR / f"grade_{name}.pkl")
        print(f"[grade/{name}] MAE={metrics['mae']} RMSE={metrics['rmse']} R2={metrics['r2']}")
        results.append({"task": "grade", "model_name": name, **metrics})

    for name, model in RISK_MODELS.items():
        pipe = Pipeline([("scaler", StandardScaler()), ("clf", model)])
        pipe.fit(X_tr_r, y_tr_r)
        metrics = evaluate_classification(pipe, X_te_r, y_te_r)
        joblib.dump(pipe, MODELS_DIR / f"risk_{name}.pkl")
        print(f"[risk/{name}]  ACC={metrics['accuracy']} F1={metrics['f1']} AUC={metrics['roc_auc']}")
        results.append({"task": "risk", "model_name": name, **metrics})

    if db_session:
        from app.models.prediction import ModelMetric
        from datetime import datetime
        db_session.query(ModelMetric).delete()
        for r in results:
            db_session.add(ModelMetric(**r))
        db_session.commit()

    return results

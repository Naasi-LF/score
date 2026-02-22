# 学生成绩分析与预测系统

Full-stack student score analysis and prediction system. FastAPI + Vue 3 + PostgreSQL + scikit-learn, containerized with Docker Compose.

## Quick Start

### 1. Start all services

```bash
docker compose up --build -d
```

### 2. Train ML models

Place the dataset file at `backend/ml/datasets/student-mat.csv`, then:

```bash
docker compose exec backend python ml/train_all.py
```

> The dataset is the UCI Student Performance dataset. Download from: https://archive.ics.uci.edu/dataset/320/student+performance

### 3. Access

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| Backend API docs | http://localhost:8000/docs |

Default credentials: `admin` / `admin123`

---

## Features

- **Dashboard** — student count, average scores, grade distribution charts
- **Student Management** — add, delete, paginate, bulk import via CSV/Excel
- **Single Prediction** — predict G3 grade (regression) or risk level (classification) for one student
- **Batch Prediction** — upload CSV, get predictions for all rows, download results
- **Prediction History** — browse all past predictions with filters
- **Model Comparison** — compare MAE/RMSE/R² (regression) or Accuracy/F1/ROC-AUC (classification) across 4 models, view feature importance

## ML Models

Two task types, four models each:

| Task | Models |
|------|--------|
| Grade prediction (regression) | Random Forest, SVM, Decision Tree, Linear Regression |
| Risk warning (classification) | Random Forest, SVM, Decision Tree, Logistic Regression |

Models are saved to `backend/ml/saved_models/` as `{task}_{model_name}.pkl`.

---

## Rebuild a single service

```bash
docker compose up --build -d backend
docker compose up --build -d frontend
```

## View logs

```bash
docker compose logs -f backend
docker compose logs -f frontend
```

## Stop everything

```bash
docker compose down
```

To also remove the database volume:

```bash
docker compose down -v
```

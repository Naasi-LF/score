# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Full-stack Student Score Analysis & Prediction System. FastAPI backend + Vue 3 frontend + PostgreSQL + scikit-learn ML models, all containerized with Docker Compose.

## Commands

### Start everything
```bash
docker compose up --build -d
```

### Train ML models (required after first start, needs dataset)
```bash
# Place student-mat.csv in backend/ml/datasets/ first
docker compose exec backend python ml/train_all.py
```

### View logs
```bash
docker compose logs -f backend
docker compose logs -f frontend
```

### Rebuild a single service
```bash
docker compose up --build -d backend
```

### Access
- Frontend: http://localhost:3000
- Backend API docs: http://localhost:8000/docs
- Default credentials: `admin` / `admin123`

## Architecture

### Backend (`backend/`)
FastAPI app with SQLAlchemy ORM and PostgreSQL. Entry point is `app/main.py` — creates tables on startup and seeds the admin user.

- `app/api/` — route handlers (auth, students, predictions, analytics)
- `app/models/` — SQLAlchemy models: User, Student, Prediction, ModelMetric
- `app/services/` — business logic: `auth_service.py` (JWT + bcrypt), `student_service.py`, `ml_service.py` (model loading/inference)
- `app/schemas/` — Pydantic v2 request/response schemas
- `app/config.py` — settings loaded from env vars

### ML Pipeline (`backend/ml/`)
- `preprocessor.py` — defines `FEATURE_COLS`, `ENCODING` dict for categorical features (sex, address, famsize, activities), and `prepare_dataset()`
- `trainer.py` — trains 4 grade models (regression) + 4 risk models (classification), saves as `{task}_{model_name}.pkl` via joblib
- `ml_service.py` — loads pipelines at inference time; **must apply `ENCODING` map before building feature vector** (categorical strings like "M"/"F" must be encoded to int before StandardScaler)
- Models saved to `ml/saved_models/`, dataset expected at `ml/datasets/student-mat.csv`

### Frontend (`frontend/src/`)
Vue 3 + Vite + Pinia + Vue Router + Element Plus + ECharts (vue-echarts).

- `api/index.js` — Axios instance; attaches JWT from Pinia auth store, redirects to `/login` on 401
- `stores/auth.js` — Pinia store for login state and token
- `router/index.js` — guards all routes except `/login` with auth check
- `views/` — 8 pages: Login, Layout (shell), Dashboard, Students, Prediction, BatchPrediction, History, ModelComparison

### Key Constraints
- `bcrypt==4.0.1` pinned alongside `passlib[bcrypt]==1.7.4` — do not upgrade bcrypt or passlib without testing; newer bcrypt breaks passlib compatibility
- pip uses Tsinghua mirror in Dockerfile (`https://pypi.tuna.tsinghua.edu.cn/simple/`) with `--timeout 120 --retries 5`
- Feature encoding: categorical columns must go through `ENCODING` dict in `preprocessor.py` at both train time and inference time — raw strings will crash the scaler

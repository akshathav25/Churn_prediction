# Project Rules

- Stack: Next.js (React, TypeScript) frontend; FastAPI (Python 3.11) backend.
- ML: scikit-learn Pipeline with ColumnTransformer (OneHotEncoder for categoricals, StandardScaler for numerics).
- Model: Start with LogisticRegression; also expose a switch for RandomForest.
- Paths: data/churn.csv for training; save model to model/model.joblib.
- APIs:
  - POST /train: trains on data/churn.csv, returns metrics (accuracy, precision, recall, f1), and saves model.
  - POST /predict: body = single JSON record; returns prediction + probability.
  - POST /predict-batch: multipart/form-data with a CSV file; returns CSV predictions.
- Frontend routes:
  - / (dashboard): buttons to Train, Upload Test CSV, Download Results.
  - /predict (form): manual single prediction (fields auto-generated from columns).
- UX: show confusion matrix & ROC-AUC after training; show preview table of batch predictions.
- Dev:
  - Root: /backend (FastAPI), /frontend (Next.js).
  - Provide package scripts for dev: `pnpm dev` (frontend), `uvicorn` for backend, and a root README with setup steps.

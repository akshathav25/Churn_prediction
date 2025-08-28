from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix
import joblib
import os
import tempfile
from typing import Dict, List, Any, Optional
import io

app = FastAPI(
    title="Churn Analysis API",
    description="API for customer churn prediction and analysis with automatic model training",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

model = None
pipeline = None
feature_columns = None
target_column = None
categorical_columns = None
numerical_columns = None
categorical_values: Optional[Dict[str, List[str]]] = None

class PredictionInput(BaseModel):
    pass

class PredictionResponse(BaseModel):
    prediction: int
    probability: float

class TrainingResponse(BaseModel):
    message: str
    metrics: Dict[str, Any]
    target_column: str
    feature_columns: List[str]
    categorical_columns: List[str]
    numerical_columns: List[str]

def detect_column_types(df: pd.DataFrame) -> tuple[List[str], List[str]]:
    numerical: List[str] = []
    categorical: List[str] = []
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            # treat low-cardinality integers as categorical
            if pd.api.types.is_integer_dtype(df[col]) and df[col].nunique(dropna=True) <= 10:
                categorical.append(col)
            else:
                numerical.append(col)
        else:
            categorical.append(col)
    return numerical, categorical

def detect_target_column(df: pd.DataFrame, target_param: Optional[str] = None) -> str:
    if target_param:
        if target_param in df.columns:
            return target_param
        raise ValueError(f"Target column '{target_param}' not found in dataset")
    for candidate in ["Churn", "Exited", "churn", "target"]:
        if candidate in df.columns:
            return candidate
    raise ValueError("No target column found. Please specify with ?target= parameter")

def create_pipeline(categorical_cols: List[str], numerical_cols: List[str]):
    preprocessors = []
    if categorical_cols:
        preprocessors.append(
            ('cat', OneHotEncoder(drop='first', sparse_output=False, handle_unknown='ignore'), categorical_cols)
        )
    if numerical_cols:
        preprocessors.append(
            ('num', StandardScaler(), numerical_cols)
        )
    if not preprocessors:
        raise ValueError("No features found for preprocessing")
    column_transformer = ColumnTransformer(
        transformers=preprocessors,
        remainder='drop'
    )
    return Pipeline([
        ('preprocessor', column_transformer),
        ('classifier', LogisticRegression(random_state=42, max_iter=1000))
    ])

@app.on_event("startup")
async def startup_event():
    global model, pipeline, feature_columns, target_column, categorical_columns, numerical_columns, categorical_values
    model_path = "model/model.joblib"
    if os.path.exists(model_path):
        try:
            model_data = joblib.load(model_path)
            pipeline = model_data.get("pipeline")
            feature_columns = model_data.get("feature_columns")
            target_column = model_data.get("target_column")
            categorical_columns = model_data.get("categorical_columns")
            numerical_columns = model_data.get("numerical_columns")
            categorical_values = model_data.get("categorical_values")
            print("Model loaded successfully from model/model.joblib")
        except Exception as e:
            print(f"Error loading model: {e}")
    else:
        print("Model not found; API will serve /train to create one")

@app.get("/")
async def root():
    return {"message": "Churn Analysis API is running", "status": "healthy"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "model_loaded": pipeline is not None
    }

@app.get("/schema")
async def get_schema():
    global feature_columns, target_column, categorical_columns, numerical_columns, categorical_values
    if feature_columns is None:
        # attempt to read from saved model
        model_path = "model/model.joblib"
        if os.path.exists(model_path):
            try:
                model_data = joblib.load(model_path)
                feature_columns = model_data.get("feature_columns")
                target_column = model_data.get("target_column")
                categorical_columns = model_data.get("categorical_columns")
                numerical_columns = model_data.get("numerical_columns")
                categorical_values = model_data.get("categorical_values")
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Unable to load schema: {e}")
        else:
            raise HTTPException(status_code=400, detail="Schema not available. Train the model first.")
    fields = []
    for col in feature_columns:
        if categorical_columns and col in categorical_columns:
            fields.append({
                "name": col,
                "type": "categorical",
                "values": (categorical_values or {}).get(col, [])
            })
        else:
            fields.append({
                "name": col,
                "type": "number"
            })
    return {
        "target": target_column,
        "fields": fields
    }

@app.post("/train", response_model=TrainingResponse)
async def train_model(target: Optional[str] = None):
    global model, pipeline, feature_columns, target_column, categorical_columns, numerical_columns, categorical_values
    try:
        data_path = "../data/Churn_Modelling.csv"
        if not os.path.exists(data_path):
            raise HTTPException(status_code=404, detail="Data file not found. Please ensure data/Churn_Modelling.csv exists.")
        df = pd.read_csv(data_path)
        target_column = detect_target_column(df, target)
        feature_columns = [c for c in df.columns if c != target_column and not c.lower().endswith('id')]
        numerical_columns, categorical_columns = detect_column_types(df[feature_columns])
        # collect categorical values for schema
        categorical_values = {c: sorted([str(v) for v in pd.Series(df[c]).dropna().unique().tolist()]) for c in (categorical_columns or [])}
        X = df[feature_columns]
        y = df[target_column]
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
        pipeline = create_pipeline(categorical_columns, numerical_columns)
        pipeline.fit(X_train, y_train)
        y_pred = pipeline.predict(X_test)
        y_proba = pipeline.predict_proba(X_test)[:, 1]
        metrics: Dict[str, Any] = {
            "accuracy": float(accuracy_score(y_test, y_pred)),
            "precision": float(precision_score(y_test, y_pred, zero_division=0)),
            "recall": float(recall_score(y_test, y_pred, zero_division=0)),
            "f1_score": float(f1_score(y_test, y_pred, zero_division=0)),
            "roc_auc": float(roc_auc_score(y_test, y_proba))
        }
        cm = confusion_matrix(y_test, y_pred)
        metrics["confusion_matrix"] = {
            "true_negatives": int(cm[0, 0]),
            "false_positives": int(cm[0, 1]),
            "false_negatives": int(cm[1, 0]),
            "true_positives": int(cm[1, 1])
        }
        os.makedirs("model", exist_ok=True)
        joblib.dump({
            "pipeline": pipeline,
            "feature_columns": feature_columns,
            "target_column": target_column,
            "categorical_columns": categorical_columns,
            "numerical_columns": numerical_columns,
            "categorical_values": categorical_values
        }, "model/model.joblib")
        model = pipeline
        return TrainingResponse(
            message="Model trained successfully",
            metrics=metrics,
            target_column=target_column,
            feature_columns=feature_columns,
            categorical_columns=categorical_columns,
            numerical_columns=numerical_columns
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Training error: {str(e)}")

@app.post("/predict", response_model=PredictionResponse)
async def predict_single(input_data: Dict[str, Any]):
    global pipeline, feature_columns
    if pipeline is None:
        raise HTTPException(
            status_code=400, 
            detail="Model not trained yet. Please train the model first using the /train endpoint."
        )
    try:
        df_input = pd.DataFrame([input_data])
        
        # Check for missing required columns
        missing = set(feature_columns) - set(df_input.columns)
        if missing:
            raise HTTPException(
                status_code=400, 
                detail=f"Missing required columns: {list(missing)}. Please ensure your input includes all required fields: {feature_columns}"
            )
        
        # Check for extra columns (warn but don't fail)
        extra = set(df_input.columns) - set(feature_columns)
        if extra:
            print(f"Warning: Extra columns provided: {list(extra)}. These will be ignored.")
        
        df_input = df_input[feature_columns]
        
        # Validate data types for numerical columns
        if numerical_columns:
            for col in numerical_columns:
                if col in df_input.columns:
                    try:
                        df_input[col] = pd.to_numeric(df_input[col], errors='raise')
                    except (ValueError, TypeError):
                        raise HTTPException(
                            status_code=400,
                            detail=f"Column '{col}' must be numeric. Received: {df_input[col].iloc[0]}"
                        )
        
        pred = pipeline.predict(df_input)[0]
        proba = pipeline.predict_proba(df_input)[0, 1]
        return PredictionResponse(prediction=int(pred), probability=float(proba))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@app.post("/predict-batch")
async def predict_batch(file: UploadFile = File(...)):
    global pipeline, feature_columns
    if pipeline is None:
        raise HTTPException(
            status_code=400, 
            detail="Model not trained yet. Please train the model first using the /train endpoint."
        )
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV file. Please upload a .csv file.")
    try:
        content = await file.read()
        df = pd.read_csv(io.StringIO(content.decode('utf-8')))
        
        # Check for missing required columns
        missing = set(feature_columns) - set(df.columns)
        if missing:
            raise HTTPException(
                status_code=400, 
                detail=f"CSV is missing required columns: {list(missing)}. Your CSV must include all required columns: {feature_columns}"
            )
        
        # Check for extra columns (warn but don't fail)
        extra = set(df.columns) - set(feature_columns)
        if extra:
            print(f"Warning: CSV contains extra columns: {list(extra)}. These will be ignored during prediction.")
        
        df_features = df[feature_columns]
        
        # Validate data types for numerical columns
        if numerical_columns:
            for col in numerical_columns:
                if col in df_features.columns:
                    try:
                        df_features[col] = pd.to_numeric(df_features[col], errors='raise')
                    except (ValueError, TypeError):
                        raise HTTPException(
                            status_code=400,
                            detail=f"Column '{col}' must contain only numeric values. Found non-numeric values in your CSV."
                        )
        
        preds = pipeline.predict(df_features)
        probas = pipeline.predict_proba(df_features)[:, 1]
        df_out = df.copy()
        df_out['Prediction'] = preds
        df_out['Probability'] = probas
        
        # Convert to CSV string
        csv_content = df_out.to_csv(index=False)
        
        # Create streaming response with proper headers
        return StreamingResponse(
            io.StringIO(csv_content),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=predictions_{file.filename}",
                "Content-Type": "text/csv; charset=utf-8"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch prediction error: {str(e)}")

@app.get("/model-info")
async def get_model_info():
    if pipeline is None:
        return {"error": "Model not trained"}
    return {
        "target_column": target_column,
        "feature_columns": feature_columns,
        "categorical_columns": categorical_columns,
        "numerical_columns": numerical_columns,
        "model_type": type(pipeline.named_steps['classifier']).__name__
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

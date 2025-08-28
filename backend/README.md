# Churn Analysis Backend

FastAPI backend for customer churn prediction with automatic model training and inference.

## Features

- **Automatic Model Training**: Train models from CSV data with automatic column type detection
- **Single Prediction**: Make predictions for individual customer records
- **Batch Prediction**: Process multiple records from CSV files
- **Model Persistence**: Save and load trained models
- **Comprehensive Metrics**: Accuracy, precision, recall, F1-score, ROC-AUC, confusion matrix
- **Graceful Error Handling**: Clear error messages for missing models and column mismatches

## Environment Setup

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Installation

1. **Clone the repository and navigate to backend:**

   ```bash
   cd backend
   ```

2. **Create virtual environment:**

   ```bash
   python -m venv venv
   ```

3. **Activate virtual environment:**

   - **Windows:**
     ```bash
     venv\Scripts\activate
     ```
   - **macOS/Linux:**
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

5. **Copy environment file:**

   ```bash
   cp .env.example .env
   ```

6. **Edit .env file with your configuration:**
   ```bash
   # Backend Configuration
   HOST=0.0.0.0
   PORT=8000
   DEBUG=true
   CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
   ```

## Running the Server

### Development Mode

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Using Python directly

```bash
python main.py
```

## API Endpoints

### Health & Information

#### GET /health

Health check endpoint.

```bash
curl http://localhost:8000/health
```

#### GET /schema

Get model schema and field information.

```bash
curl http://localhost:8000/schema
```

#### GET /model-info

Get information about the trained model.

```bash
curl http://localhost:8000/model-info
```

### Training

#### POST /train

Train the churn prediction model.

**Basic training:**

```bash
curl -X POST "http://localhost:8000/train"
```

**Training with custom target column:**

```bash
curl -X POST "http://localhost:8000/train?target=Exited"
```

**Response includes:**

- Training metrics (accuracy, precision, recall, F1, ROC-AUC)
- Confusion matrix
- Feature column information
- Model configuration details

### Prediction

#### POST /predict

Single record prediction.

**Example request:**

```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "CreditScore": 600,
    "Geography": "France",
    "Gender": "Male",
    "Age": 35,
    "Tenure": 5,
    "Balance": 100000,
    "NumOfProducts": 2,
    "HasCrCard": 1,
    "IsActiveMember": 1,
    "EstimatedSalary": 50000
  }'
```

**Response:**

```json
{
  "prediction": 0,
  "probability": 0.1234
}
```

#### POST /predict-batch

Batch prediction from CSV file.

**Example request:**

```bash
curl -X POST "http://localhost:8000/predict-batch" \
  -F "file=@your_data.csv"
```

**Response:** CSV file download with original data + predictions

## Error Handling

### Common Error Scenarios

1. **Model Not Trained:**

   ```
   HTTP 400: Model not trained yet. Please train the model first using the /train endpoint.
   ```

2. **Missing Required Columns:**

   ```
   HTTP 400: Missing required columns: ['CreditScore', 'Geography'].
   Please ensure your input includes all required fields: ['CreditScore', 'Geography', ...]
   ```

3. **Invalid Data Types:**

   ```
   HTTP 400: Column 'Age' must be numeric. Received: "thirty-five"
   ```

4. **File Type Validation:**
   ```
   HTTP 400: File must be a CSV file. Please upload a .csv file.
   ```

## Data Requirements

### Training Data Format

- **File:** CSV format
- **Target Column:** Auto-detected from: `["Churn", "Exited", "churn", "target"]`
- **Features:** Automatically detected as numerical or categorical
- **Encoding:** UTF-8 recommended

### Prediction Input Format

- **Single:** JSON with all required feature columns
- **Batch:** CSV with same schema as training data
- **Data Types:** Numerical columns must contain numbers, categorical columns must match training values

## Model Architecture

- **Preprocessing:** ColumnTransformer with OneHotEncoder for categoricals, StandardScaler for numericals
- **Classifier:** LogisticRegression with optimized hyperparameters
- **Pipeline:** sklearn Pipeline for seamless preprocessing + prediction
- **Validation:** Stratified train/test split to maintain class balance
- **Persistence:** Model saved to `model/model.joblib` after training

## Development

### Project Structure

```
backend/
├── main.py              # FastAPI application
├── requirements.txt     # Python dependencies
├── test_api.py         # API test script
├── README.md           # This file
├── .env.example        # Environment configuration template
└── model/              # Model storage directory (created automatically)
    └── model.joblib    # Trained model file
```

### Testing

Run the test script to verify API functionality:

```bash
python test_api.py
```

### Logging

The application provides detailed logging for:

- Model training progress
- Column type detection
- Data validation warnings
- Error details

## Configuration

### Environment Variables

- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8000)
- `DEBUG`: Debug mode (default: true)
- `CORS_ORIGINS`: Allowed CORS origins (comma-separated)

### Model Storage

- Models are automatically saved to `model/model.joblib`
- Includes pipeline, feature columns, and metadata
- Automatically loaded on server startup

## Troubleshooting

### Common Issues

1. **Port already in use:**

   ```bash
   # Change port in command or .env file
   uvicorn main:app --port 8001
   ```

2. **Model not loading:**

   - Check if `model/model.joblib` exists
   - Verify file permissions
   - Check console for error messages

3. **CSV upload fails:**

   - Ensure file is valid CSV
   - Check column names match training data
   - Verify data types are correct

4. **Memory issues with large files:**
   - Consider chunking large CSV files
   - Monitor system memory usage
   - Use streaming responses for large datasets

## API Documentation

Once the server is running, access interactive documentation at:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## Support

For issues and questions:

1. Check the error messages and logs
2. Verify data format and requirements
3. Ensure all dependencies are installed
4. Check the API documentation at `/docs`

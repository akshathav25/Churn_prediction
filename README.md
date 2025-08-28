# Churn Analysis Monorepo

This monorepo contains both the frontend and backend applications for the Churn Analysis project.

## Project Structure

```
churn/
├── frontend/          # Next.js + TypeScript frontend
├── backend/           # FastAPI + Python backend
├── data/              # Data files
├── .gitignore         # Git ignore rules
├── Makefile           # Unix/Linux development commands
├── setup-dev.ps1      # Windows PowerShell setup script
└── README.md          # This file
```

## Prerequisites

- **Node.js** (v18 or higher)
- **Python** (v3.8 or higher)
- **pnpm** (for frontend package management)
- **pip** (for Python package management)

## Environment Setup

### Backend Environment

1. **Navigate to backend directory:**

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

5. **Create environment file:**
   ```bash
   # Create .env file with your configuration
   echo "HOST=0.0.0.0" > .env
   echo "PORT=8000" >> .env
   echo "DEBUG=true" >> .env
   echo "CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000" >> .env
   ```

### Frontend Environment

1. **Navigate to frontend directory:**

   ```bash
   cd frontend
   ```

2. **Install dependencies:**

   ```bash
   pnpm install
   ```

3. **Create environment file:**
   ```bash
   # Create .env.local file with your configuration
   echo "NEXT_PUBLIC_API_BASE=http://localhost:8000" > .env.local
   echo "NEXT_PUBLIC_APP_NAME=Churn Analysis Dashboard" >> .env.local
   echo "NEXT_PUBLIC_APP_VERSION=1.0.0" >> .env.local
   ```

## Quick Start

### Backend (FastAPI)

1. **Start the server:**

   ```bash
   cd backend
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Verify it's running:**
   ```bash
   curl http://localhost:8000/health
   ```

The backend will be available at `http://localhost:8000`

### Frontend (Next.js)

1. **Start the development server:**
   ```bash
   cd frontend
   pnpm dev
   ```

The frontend will be available at `http://localhost:3000`

## API Endpoints & Examples

### Health & Information

#### Health Check

```bash
curl http://localhost:8000/health
```

#### Get Model Schema

```bash
curl http://localhost:8000/schema
```

#### Get Model Info

```bash
curl http://localhost:8000/model-info
```

### Training

#### Train Model (Basic)

```bash
curl -X POST "http://localhost:8000/train"
```

#### Train Model (Custom Target)

```bash
curl -X POST "http://localhost:8000/train?target=Exited"
```

**Response includes:**

- Training metrics (accuracy, precision, recall, F1, ROC-AUC)
- Confusion matrix
- Feature column information
- Model configuration details

### Prediction

#### Single Record Prediction

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

#### Batch Prediction from CSV

```bash
curl -X POST "http://localhost:8000/predict-batch" \
  -F "file=@your_data.csv"
```

**Response:** CSV file download with original data + predictions

## Development

### Backend Development

- The FastAPI server runs with auto-reload enabled
- API documentation is available at `http://localhost:8000/docs`
- ReDoc documentation at `http://localhost:8000/redoc`
- Comprehensive error handling with clear messages
- Automatic column type detection and validation

### Frontend Development

- Next.js hot reload is enabled
- TypeScript compilation runs automatically
- ESLint and Prettier are configured
- Dynamic form generation based on backend schema
- Real-time preview and download for batch predictions

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

## Model Features

- **Automatic Column Detection**: Automatically identifies numerical vs categorical columns
- **Target Column Detection**: Auto-detects target column from common names (Churn, Exited, churn, target)
- **Pipeline Architecture**: Uses sklearn Pipeline with ColumnTransformer for preprocessing
- **Stratified Split**: Maintains class balance in train/test split
- **Comprehensive Metrics**: Accuracy, precision, recall, F1-score, ROC-AUC, confusion matrix
- **Model Persistence**: Saves trained model to `model/model.joblib`
- **Graceful Error Handling**: Clear error messages for missing models and column mismatches

## Development Commands

### Using Makefile (Unix/Linux/Mac)

```bash
make install          # Install all dependencies
make dev             # Run both backend and frontend
make run-backend     # Run only backend
make run-frontend    # Run only frontend
make clean           # Clean up generated files
```

### Using PowerShell Script (Windows)

```powershell
.\setup-dev.ps1      # Setup development environment
```

### Manual Commands

```bash
# Backend
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Frontend
cd frontend
pnpm dev
```

## Testing

### Backend Testing

```bash
cd backend
python test_api.py
```

### Frontend Testing

```bash
cd frontend
pnpm test
```

## Configuration

### Backend Environment Variables

- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8000)
- `DEBUG`: Debug mode (default: true)
- `CORS_ORIGINS`: Allowed CORS origins (comma-separated)

### Frontend Environment Variables

- `NEXT_PUBLIC_API_BASE`: Backend API URL (default: http://localhost:8000)
- `NEXT_PUBLIC_APP_NAME`: Application name
- `NEXT_PUBLIC_APP_VERSION`: Application version

## Troubleshooting

### Common Issues

1. **Port already in use:**

   - Change port in backend command or .env file
   - Update frontend API_BASE_URL accordingly

2. **Model not loading:**

   - Check if `backend/model/model.joblib` exists
   - Verify file permissions
   - Check console for error messages

3. **CSV upload fails:**

   - Ensure file is valid CSV
   - Check column names match training data
   - Verify data types are correct

4. **Frontend can't connect to backend:**
   - Verify backend is running
   - Check CORS configuration
   - Verify API_BASE_URL in frontend .env.local

## Contributing

1. Create a feature branch
2. Make your changes
3. Test both frontend and backend
4. Submit a pull request

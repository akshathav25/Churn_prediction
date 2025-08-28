#!/usr/bin/env python3
"""
Test script for the Churn Analysis API
Run this after starting the backend server
"""

import requests
import json
import pandas as pd
from io import StringIO

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("Testing /health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_train():
    """Test training endpoint"""
    print("Testing /train endpoint...")
    response = requests.post(f"{BASE_URL}/train")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Training successful!")
        print(f"Target column: {data['target_column']}")
        print(f"Feature columns: {data['feature_columns']}")
        print(f"Metrics: {json.dumps(data['metrics'], indent=2)}")
    else:
        print(f"Error: {response.text}")
    print()

def test_model_info():
    """Test model info endpoint"""
    print("Testing /model-info endpoint...")
    response = requests.get(f"{BASE_URL}/model-info")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Model info: {json.dumps(data, indent=2)}")
    else:
        print(f"Error: {response.text}")
    print()

def test_predict():
    """Test single prediction endpoint"""
    print("Testing /predict endpoint...")
    
    # Sample data (adjust based on your actual feature columns)
    sample_data = {
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
    }
    
    response = requests.post(f"{BASE_URL}/predict", json=sample_data)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Prediction: {data['prediction']}")
        print(f"Probability: {data['probability']:.4f}")
    else:
        print(f"Error: {response.text}")
    print()

def test_predict_batch():
    """Test batch prediction endpoint"""
    print("Testing /predict-batch endpoint...")
    
    # Create sample CSV data
    sample_data = pd.DataFrame({
        "CreditScore": [600, 700, 500],
        "Geography": ["France", "Germany", "Spain"],
        "Gender": ["Male", "Female", "Male"],
        "Age": [35, 40, 30],
        "Tenure": [5, 3, 7],
        "Balance": [100000, 150000, 80000],
        "NumOfProducts": [2, 1, 3],
        "HasCrCard": [1, 1, 0],
        "IsActiveMember": [1, 0, 1],
        "EstimatedSalary": [50000, 60000, 45000]
    })
    
    # Convert to CSV string
    csv_buffer = StringIO()
    sample_data.to_csv(csv_buffer, index=False)
    csv_content = csv_buffer.getvalue()
    
    # Send file
    files = {'file': ('test_data.csv', csv_content, 'text/csv')}
    response = requests.post(f"{BASE_URL}/predict-batch", files=files)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("Batch prediction successful!")
        print(f"Response headers: {dict(response.headers)}")
        # Save the response to a file
        with open("batch_predictions.csv", "wb") as f:
            f.write(response.content)
        print("Saved predictions to batch_predictions.csv")
    else:
        print(f"Error: {response.text}")
    print()

def main():
    """Run all tests"""
    print("Churn Analysis API Test Suite")
    print("=" * 40)
    print()
    
    try:
        test_health()
        test_train()
        test_model_info()
        test_predict()
        test_predict_batch()
        
        print("All tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the API server.")
        print("Make sure the backend is running with: uvicorn main:app --reload --host 0.0.0.0 --port 8000")
    except Exception as e:
        print(f"Error during testing: {e}")

if __name__ == "__main__":
    main()

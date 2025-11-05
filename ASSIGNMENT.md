# ASSIGNMENT.md

## Overview

This document provides a comprehensive explanation of the solution implemented for the ML engineering challenge. The task was to predict the total money a passenger will spend on trips within 30 days of registration, using their activity in the first 7 days, and to serve this prediction via an HTTP API while tracking requests.

The solution includes model training, API serving, and request logging, all containerized for easy deployment.

**Problem Context**: The challenge requires building an end-to-end ML system that can predict customer lifetime value (CLV) for ride-sharing passengers. Given features like recency (days since last trip), frequency (number of trips), and monetary value (total spent) in the first 7 days, we need to predict spending in the next 30 days. The system must be production-ready with proper API endpoints and request tracking.

**Solution Approach**: We implement a machine learning pipeline using scikit-learn, serve predictions via a FastAPI REST API, and track all requests in a SQLite database. Everything is containerized with Docker for reproducibility and easy deployment.

**Additional Files:**
- `EXTRA_ANALYSIS.md`: Extra validation analysis comparing model predictions with actual passenger data
- `validate_predictions.py`: Python script used for prediction validation analysis

---

## Solution Summary

### 1. Model Training
- **Data Source**: SQLite database (`database.sqlite`) with passenger activity features: `recency_7`, `frequency_7`, `monetary_value_7`, and target `monetary_value_30`.
- **Models Evaluated**: Linear Regression, Ridge Regression, and Random Forest Regressor.
- **Hyperparameter Tuning**: Used GridSearchCV for each model to find optimal parameters.
- **Best Model Selection**: Random Forest Regressor with `max_depth=5`, `min_samples_split=2`, `n_estimators=100`, achieving the lowest test MSE (1827.28).
- **Output**: Trained model saved as `model.joblib`, with results logged in `model_results.csv`.

**Why Random Forest?** Random Forest was chosen as it typically handles non-linear relationships well and is less prone to overfitting compared to single decision trees. The hyperparameter tuning ensures optimal performance.

### 2. Model Serving
- **Framework**: FastAPI for building the REST API.
- **Endpoints**:
  - `GET /health`: Health check.
  - `POST /api/predict`: Accepts passenger features and returns predicted `monetary_value_30`.
  - `GET /api/requests/{passenger_id}`: Returns the count of prediction requests for a given passenger.
  - `POST /reset`: Resets all prediction request counts (for testing).
- **Model Loading**: Model is loaded at application startup for efficient serving.
- **Error Handling**: Returns appropriate HTTP status codes (e.g., 503 if model is unavailable).

**Why FastAPI?** FastAPI provides automatic API documentation, type validation, and high performance with async support, making it ideal for ML serving.

### 3. Request Tracking
- **Database**: New table `prediction_requests` in SQLite to log each prediction request, including passenger ID, input features, prediction, and timestamp.
- **Implementation**: Every call to `/api/predict` inserts a record into this table.
- **Persistence**: Database changes are persisted using Docker volumes, ensuring request history is maintained across container restarts.
- **Querying**: The `/api/requests/{passenger_id}` endpoint queries the count of requests for the specified passenger.

**Database Schema**:
```sql
CREATE TABLE prediction_requests (
    id INTEGER PRIMARY KEY,
    passenger_id INTEGER,
    recency_7 INTEGER,
    frequency_7 INTEGER,
    monetary_7 REAL,
    prediction REAL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Testing Approach
- **Framework**: pytest with FastAPI TestClient
- **Coverage**: 14 test cases covering:
  - API health checks
  - Successful predictions with various inputs
  - Request counting accuracy
  - Data isolation between passengers
  - Error handling for invalid inputs
- **Docker Integration**: Tests run in isolated containers to ensure environment consistency
- **Database Testing**: Uses in-memory SQLite for test isolation

**Test Categories**:
- **Health Tests**: Verify API startup and basic connectivity
- **Prediction Tests**: Test model loading, input validation, and prediction accuracy
- **Tracking Tests**: Ensure request logging and counting work correctly
- **Isolation Tests**: Confirm data separation between different passengers

---

## Implementation Details

### Docker Configuration
- **Multi-stage builds**: Separate stages for base, test, train, and app environments.
- **Volume mounts**: Database file is mounted as a volume to persist prediction request data across container restarts.
- **Service isolation**: Different services for training, testing, and serving with appropriate file access.

**Docker Architecture**:
- `base`: Common dependencies and setup
- `train`: Runs model training and saves model files
- `app`: Serves the API with model loading
- `test`: Runs unit tests

### Key Technologies
- **Python 3.10**: Core language.
- **FastAPI**: For API development.
- **SQLAlchemy**: ORM for database interactions.
- **Scikit-learn**: For machine learning models and GridSearchCV.
- **Pandas**: Data manipulation.
- **Joblib**: Model serialization.
- **Poetry**: Dependency management.
- **Docker**: Containerization.

### Model Training Process
1. Load data from SQLite.
2. Split into train/test sets (80/20).
3. For each model, perform GridSearchCV with predefined parameter grids.
4. Evaluate on test set using MSE.
5. Select and save the model with the lowest MSE.
6. Log results to CSV for transparency.

**GridSearchCV Details**:
- Linear Regression: Tests `fit_intercept` [True, False]
- Ridge: Tests `alpha` [0.1, 1.0, 10.0] and `fit_intercept` [True, False]
- Random Forest: Tests `n_estimators` [50, 100, 200], `max_depth` [None, 5, 10], `min_samples_split` [2, 5]

### API Startup
- On startup, create database tables if needed.
- Load the trained model from disk.
- If model loading fails, log error and set model to None (API will return 503).

### Prediction Flow
1. Receive POST request with passenger features.
2. Validate input using Pydantic models.
3. Make prediction using loaded model.
4. Log request details to database.
5. Return prediction response.

**Input Validation**: Uses Pydantic BaseModel to ensure correct data types and required fields.

**Model Compatibility**: Converts input to pandas DataFrame with proper column names to avoid sklearn warnings about feature names.

### API Endpoints Details

#### Health Check (`GET /health`)
- **Purpose**: Verify API availability
- **Response**: Simple string "healthy"
- **Use**: Load balancers or monitoring systems can use this to check service health

#### Prediction (`POST /api/predict`)
- **Input**: JSON with passenger features
- **Validation**: Ensures all required fields are present and correctly typed
- **Processing**: 
  - Converts features to DataFrame for sklearn compatibility
  - Makes prediction using loaded model
  - Logs request to database with timestamp
- **Output**: Passenger ID and predicted monetary value for next 30 days

#### Request Count (`GET /api/requests/{passenger_id}`)
- **Purpose**: Track API usage per passenger
- **Processing**: Queries database for count of predictions made for this passenger
- **Output**: Passenger ID and total request count
- **Use**: Analytics, rate limiting, or billing

#### Reset (`POST /reset`)
- **Purpose**: Clear all prediction request logs (testing utility)
- **Processing**: Deletes all records from prediction_requests table
- **Use**: Reset counts for fresh testing scenarios

---

## Changes and Justifications

### Changes Made
1. **Added Dependencies**: Included `joblib`, `scikit-learn`, `pandas` in `pyproject.toml` for ML functionality.
2. **Enhanced Training**: Upgraded from single model to multi-model comparison with GridSearchCV for better performance.
3. **Database Schema**: Added `PredictionRequest` model for request tracking.
4. **API Improvements**: Added proper error handling, input validation, and startup model loading.
5. **Containerization**: Updated Dockerfile to copy model and database files into the image.
6. **Testing**: Expanded tests to cover prediction and request tracking.
7. **File Handling**: Modified training to copy model files from container instead of volume mounts to avoid VS Code file watching issues.
8. **Documentation**: Created this comprehensive ASSIGNMENT.md.

### Justifications
- **Multi-Model Approach**: Ensures the best possible model is selected, improving prediction accuracy without excessive complexity.
- **GridSearchCV**: Automates hyperparameter tuning, leading to optimized models.
- **Request Tracking**: Provides auditability and meets the requirement for tracking API usage.
- **Docker Support**: Aligns with the original prerequisites, enabling reproducible and isolated deployments.
- **Error Handling**: Makes the API robust and user-friendly.
- **Comprehensive Testing**: Ensures reliability and catches regressions.
- **File Handling**: Prevents VS Code from incorrectly displaying model files as directories, ensuring smooth development experience.
- **Detailed Documentation**: Facilitates understanding and review of the implementation.

### Alternatives Considered
- **Jupyter Notebooks**: Considered for training but chose scripts for reproducibility via Makefile.
- **Other Frameworks**: Evaluated Flask but stuck with FastAPI for its automatic docs and async support.
- **Database Choices**: Considered PostgreSQL but used SQLite for simplicity and alignment with the provided data.

---

## Limitations

1. **Model Performance**: The best MSE (1827.28) indicates room for improvement; more features or advanced models could enhance accuracy.
2. **Data Size**: Training on a small dataset may lead to overfitting; real-world deployment would require larger, more diverse data.
3. **Scalability**: SQLite is not suitable for high-concurrency production; would need a more robust database like PostgreSQL.
4. **Error Handling**: Limited input validation; could add more comprehensive checks for edge cases.
5. **Security**: No authentication or rate limiting; production would require these.
6. **Monitoring**: No logging or metrics beyond basic request tracking.
7. **Dependencies**: Poetry and Docker add complexity; could simplify for smaller projects.
8. **Testing Coverage**: Tests are basic; more edge cases and integration tests would be ideal.
9. **Model Retraining**: No automated pipeline for retraining; manual process via Makefile.
10. **API Docs**: While FastAPI provides auto-docs, custom examples could improve usability.
11. **Database Persistence**: Uses Docker volumes for SQLite persistence; production would use proper database with backups.

---

## Results

- **Model Selection**: RandomForestRegressor outperformed others with tuned parameters.
- **API Functionality**: All endpoints working as specified, with proper responses.
- **Request Tracking**: Successfully logs and queries prediction requests.
- **Docker Deployment**: Fully containerized, runnable via `docker compose up app`.
- **Testing**: All tests pass, ensuring basic functionality.

**Model Performance**:
- Random Forest achieved MSE of 1827.28 on test set
- Linear Regression: 1907.88 MSE
- Ridge Regression: 1907.88 MSE
- Best hyperparameters found through GridSearchCV

**API Performance**:
- Fast startup with model loading
- Sub-second response times for predictions
- Proper error handling and status codes

See `model_results.csv` for detailed model comparison.

---

## How to Run

### Prerequisites
- Docker and Docker Compose installed and running.
- Ensure Docker daemon is started before running any commands.

### Setup and Run
1. Clone the repository.
2. Ensure `model.joblib` and `database.sqlite` are present (generated by training).
3. Run the Makefile commands for setup, training, and running - all commands use Docker for consistency and portability.

### Training
Run the training pipeline to generate the trained model:
```bash
make train
```

**Note**: Ensure Docker is running before executing this command.

This will:
- Build a Docker container with the training environment
- Load passenger activity data from `database.sqlite`
- Train three models: LinearRegression, Ridge, and RandomForestRegressor
- Perform GridSearchCV to find optimal hyperparameters
- Select and save the best model to `model.joblib`
- Export results to `model_results.csv`
- Clean up the container after completion

### Running the API

**Terminal 1 - Start the API server:**
```bash
make run
```

**Note**: Ensure Docker is running before executing this command.

The API will start and listen on `http://localhost:8080`. You'll see output like:
```
 running service
docker-compose down
docker-compose up --build app
[+] Building...
[+] Running 3/3
✔ mlengineer-app              Built                    0.0s 
✔ Network mlengineer_default  Created                  0.0s 
✔ Container mlengineer-app-1  Created                  0.0s 
Attaching to app-1
app-1  | INFO:     Started server process [1]
app-1  | INFO:     Waiting for application startup.
app-1  | INFO:     Application startup complete.
app-1  | INFO:     Uvicorn running on http://0.0.0.0:8080 (Press CTRL+C to quit)
app-1  | API module imported
app-1  | Startup started
app-1  | Model loaded successfully
app-1  | Startup complete
```

**Terminal 2 - Test the API endpoints:**

#### 0. Reset Request Counts (Optional - for fresh testing)
```bash
curl -s -X POST http://localhost:8080/reset | jq .
```

Expected output:
```json
{
  "message": "All prediction requests have been reset"
}
```

#### 1. Health Check Endpoint
```bash
curl -s http://localhost:8080/health | jq .
```

Expected output:
```json
"healthy"
```

#### 2. Predict Endpoint (First Request)
```bash
curl -s -X POST http://localhost:8080/api/predict \
  -H "Content-Type: application/json" \
  -d '{"id": 1234, "recency_7": 1, "frequency_7": 1, "monetary_7": 8.5}' | jq .
```

Expected output:
```json
{
  "id": 1234,
  "monetary_30": 14.28
}
```

#### 3. Check Request Count
```bash
curl -s http://localhost:8080/api/requests/1234 | jq .
```

Expected output (count after first prediction):
```json
{
  "id": 1234,
  "count": 1
}
```

#### 4. Make Another Prediction
```bash
curl -s -X POST http://localhost:8080/api/predict \
  -H "Content-Type: application/json" \
  -d '{"id": 1234, "recency_7": 3, "frequency_7": 5, "monetary_7": 25.0}' | jq .
```

Expected output:
```json
{
  "id": 1234,
  "monetary_30": 31.61
}
```

#### 5. Verify Updated Request Count
```bash
curl -s http://localhost:8080/api/requests/1234 | jq .
```

Expected output (count after second prediction):
```json
{
  "id": 1234,
  "count": 2
}
```

#### 6. Test with Different Passenger
```bash
curl -s -X POST http://localhost:8080/api/predict \
  -H "Content-Type: application/json" \
  -d '{"id": 5678, "recency_7": 2, "frequency_7": 3, "monetary_7": 12.0}' | jq .
```

Expected output:
```json
{
  "id": 5678,
  "monetary_30": 14.69
}
```

#### 7. Check Count for Different Passenger
```bash
curl -s http://localhost:8080/api/requests/5678 | jq .
```

Expected output (isolated count per passenger):
```json
{
  "id": 5678,
  "count": 1
}
```

**Important Note**: Keep the API server running in Terminal 1 while executing these test commands in Terminal 2.

### Testing
Run the complete unit test suite:
```bash
make test
```

**Note**: Ensure Docker is running before executing this command.

This will:
- Build the test container
- Run 14 comprehensive tests covering:
  - Health endpoint
  - Prediction with valid/invalid inputs
  - Request tracking and counting
  - Data isolation between passengers
  - Edge cases
- Display results and clean up containers

Expected output:
```
test/test_api.py ..............                          [100%]
============================== 14 passed in 1.13s ==============================
```

### API Documentation
Once the API is running, access the interactive Swagger documentation:
```
http://localhost:8080/docs
```

This provides a user-friendly interface to test all endpoints.

---

## Conclusion

This solution demonstrates a complete ML engineering pipeline, from data to deployment. It prioritizes simplicity, reproducibility, and best practices while meeting all challenge requirements. The use of GridSearchCV and multi-model evaluation ensures quality predictions, and the containerized API provides a production-ready serving layer.

**Key Achievements**:
- End-to-end ML pipeline with training, serving, and monitoring
- Production-ready API with proper error handling and documentation
- Comprehensive testing with 14 test cases
- Containerized deployment for easy scaling and reproducibility
- Request tracking for analytics and compliance

**Architecture Benefits**:
- **Modular Design**: Separate concerns for training, serving, and testing
- **Scalability**: Docker containers can be easily scaled horizontally
- **Maintainability**: Clear separation of ML logic, API, and data layers
- **Reproducibility**: All dependencies and configurations are containerized

**Additional Validation**: See `EXTRA_ANALYSIS.md` for extra validation analysis that compares model predictions with actual passenger data, confirming the model's real-world applicability.

For production, consider addressing the limitations mentioned, such as scaling the database and adding monitoring.

---

## Author

Parth Kalkar

Date: 2 November 2025

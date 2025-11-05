# CLV Prediction API

## Interview Take-Home Task

A complete machine learning engineering solution for predicting Customer Lifetime Value (CLV) of ride-sharing passengers. Given passenger activity in the first 7 days after registration, predict their spending in the next 30 days.

## Features

- **ML Pipeline**: Multi-model evaluation with hyperparameter tuning using GridSearchCV
- **REST API**: FastAPI-based prediction service with automatic documentation
- **Request Tracking**: SQLite database for logging and monitoring API usage
- **Containerized**: Docker deployment with multi-stage builds
- **Testing**: Comprehensive test suite with 14 test cases
- **Validation**: Extra analysis comparing predictions with actual data

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Git

### Setup and Run

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd clv-prediction-api
   ```

2. **Train the model**
   ```bash
   make train
   ```

3. **Start the API server**
   ```bash
   make run
   ```

4. **Test the API** (in another terminal)
   ```bash
   # Health check
   curl http://localhost:8080/health

   # Make prediction
   curl -X POST http://localhost:8080/api/predict \
     -H "Content-Type: application/json" \
     -d '{"id": 1234, "recency_7": 1, "frequency_7": 1, "monetary_7": 8.5}'

   # Check request count
   curl http://localhost:8080/api/requests/1234
   ```

5. **Run tests**
   ```bash
   make test
   ```

## API Endpoints

- `GET /health` - Health check
- `POST /api/predict` - Predict CLV for passenger
- `GET /api/requests/{passenger_id}` - Get request count for passenger
- `POST /reset` - Reset request counts (for testing)

## Project Structure

```
├── app/
│   ├── __init__.py
│   ├── api.py          # FastAPI application
│   ├── db.py           # Database models
│   └── training.py     # ML training pipeline
├── test/
│   ├── __init__.py
│   └── test_api.py     # API tests
├── Dockerfile          # Multi-stage Docker build
├── docker-compose.yml  # Service orchestration
├── Makefile           # Build automation
├── pyproject.toml     # Python dependencies
└── ASSIGNMENT.md      # Detailed documentation
```

## Technology Stack

- **Python 3.10**
- **FastAPI** - REST API framework
- **Scikit-learn** - Machine learning
- **SQLAlchemy** - Database ORM
- **Docker** - Containerization
- **Poetry** - Dependency management

## Model Performance

- **Best Model**: Random Forest Regressor
- **Test MSE**: 1827.28
- **Hyperparameters**: max_depth=5, min_samples_split=2, n_estimators=100

## Documentation

See [ASSIGNMENT.md](ASSIGNMENT.md) for comprehensive documentation including:
- Solution architecture and design decisions
- Implementation details and API specifications
- Testing approach and results
- Limitations and future improvements

## Development

### Local Setup (without Docker)

```bash
# Install dependencies
poetry install

# Train model
poetry run python app/training.py

# Run API
poetry run uvicorn app.api:app --host 0.0.0.0 --port 8080

# Run tests
poetry run pytest
```

### API Documentation

When the API is running, visit `http://localhost:8080/docs` for interactive Swagger documentation.

## License

This project is created for interview assessment purposes.

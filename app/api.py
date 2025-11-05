"""
extend this file for serving the HTTP endpoint
"""


print("API module imported")

from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
import joblib
import os
import pandas as pd
import warnings
from app.db import SessionLocal, get_db, PredictionRequest, create_tables
from sqlalchemy import text

# Suppress sklearn warnings about feature names
warnings.filterwarnings('ignore', category=UserWarning)

MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'model.joblib')

app = FastAPI()

model = None

@app.on_event("startup")
def startup():
    try:
        print("Startup started")
        global model
        create_tables()
        session = SessionLocal()
        session.execute(text("select 1"))
        session.close()
        if os.path.exists(MODEL_PATH):
            model = joblib.load(MODEL_PATH)
            print("Model loaded successfully")
        else:
            print("Model file not found")
            model = None
        print("Startup complete")
    except Exception as e:
        print(f"Startup error: {e}")
        raise



class PredictRequest(BaseModel):
    id: int
    recency_7: int
    frequency_7: int
    monetary_7: float



class PredictResponse(BaseModel):
    id: int
    monetary_30: float


class CountResponse(BaseModel):
    id: int
    count: int


@app.get("/health", response_model=str)
async def get_health():
    """
    check for API health
    """
    return "healthy"


@app.post("/reset")
async def reset_requests(db: Session = Depends(get_db)):
    """
    Reset all prediction request counts (for testing purposes)
    """
    db.query(PredictionRequest).delete()
    db.commit()
    return {"message": "All prediction requests have been reset"}



@app.post("/api/predict", response_model=PredictResponse)
async def predict_monetary(request_payload: PredictRequest, db: Session = Depends(get_db)):
    """
    * predict monetary value for next 30 days
    * track passenger information in dedicated table
    """
    if model is None:
        raise HTTPException(status_code=503, detail="Model not available. Please train the model first.")
    
    # Create a DataFrame with proper feature names to avoid sklearn warnings
    features_df = pd.DataFrame({
        "recency_7": [request_payload.recency_7],
        "frequency_7": [request_payload.frequency_7],
        "monetary_value_7": [request_payload.monetary_7]
    })
    
    pred = model.predict(features_df)[0]
    # Log request
    req = PredictionRequest(
        passenger_id=request_payload.id,
        recency_7=request_payload.recency_7,
        frequency_7=request_payload.frequency_7,
        monetary_7=request_payload.monetary_7,
        prediction=round(float(pred), 2)
    )
    db.add(req)
    db.commit()
    return PredictResponse(id=request_payload.id, monetary_30=round(float(pred), 2))


@app.get("/api/requests/{passenger_id}", response_model=CountResponse)
async def count_number_of_requests(
    passenger_id: int, db: Session = Depends(get_db)
):
    """
    * get the number of times this passenger id requested a prediction
    """
    count = db.query(PredictionRequest).filter(PredictionRequest.passenger_id == passenger_id).count()
    return CountResponse(id=passenger_id, count=count)

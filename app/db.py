""" This file is used for defining the database connection"""


from sqlalchemy import create_engine, Column, Integer, Float, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

engine = create_engine("sqlite:///./database.sqlite", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class PredictionRequest(Base):
    __tablename__ = "prediction_requests"
    id = Column(Integer, primary_key=True, autoincrement=True)
    passenger_id = Column(Integer, nullable=False)
    recency_7 = Column(Integer, nullable=False)
    frequency_7 = Column(Integer, nullable=False)
    monetary_7 = Column(Float, nullable=False)
    prediction = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

def create_tables():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

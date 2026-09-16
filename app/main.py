from contextlib import asynccontextmanager
from functools import lru_cache

from fastapi import APIRouter, Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db import get_session, init_db
from app.predictor import Predictor
from app.schemas import PredictionRequest, PredictionResponse
from app.service import create_prediction, get_features, get_prediction

router = APIRouter()


@lru_cache
def get_predictor():
    return Predictor(get_settings().model_path, get_settings().metadata_path)


@router.post("/predictions", response_model=PredictionResponse)
def predict(request: PredictionRequest, session: Session = Depends(get_session), predictor: Predictor = Depends(get_predictor)):
    prediction = get_prediction(session, request.request_id)
    if prediction is None:
        features = get_features(session, request.item_id)
        if features is None:
            raise HTTPException(status_code=404, detail=f"Feature not found for {request.item_id}")
        prediction = create_prediction(session, request, features, predictor)
        session.commit()  #
    return prediction


@router.get("/predictions/{request_id}", response_model=PredictionResponse)
def get_prediction_by_id(request_id: str, session: Session = Depends(get_session)):
    prediction = get_prediction(session, request_id)
    if prediction is None:
        raise HTTPException(status_code=404, detail=f"Prediction not found for {request_id}")
    return prediction


@asynccontextmanager
async def lifespan(app):
    init_db()
    get_predictor()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(router)

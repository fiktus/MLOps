from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class PredictionRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, allow_inf_nan=False)
    request_id: str = Field(min_length=1)
    item_id: str = Field(min_length=1)
    item_price: float = Field(gt=0)
    delivery_days: int = Field(ge=0)
    client_is_app: bool
    type_prepayment: Literal["card", "cash", "sbp"]


class PredictionResponse(BaseModel):
    request_id: str
    prediction: float
    model_version: str

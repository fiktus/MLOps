from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class FeatureRow(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    item_id: str = Field(min_length=1)
    historical_return_rate: float = Field(ge=0, le=1, allow_inf_nan=False)
    avg_item_losses_30d: float = Field(ge=0, allow_inf_nan=False)
    updated_at: datetime | None = None

import pytest
from app.config import get_settings
from app.predictor import Predictor

ITEM_001 = {
    "item_price": 2500.0,
    "delivery_days": 4,
    "client_is_app": True,
    "type_prepayment": "card",
    "historical_return_rate": 0.773956,
    "avg_item_losses_30d": 623.1971,
}

@pytest.fixture(scope="module")
def predictor():
    s = get_settings()
    return Predictor(s.model_path, s.metadata_path)

def test_golden_prediction(predictor):
    assert predictor.predict(ITEM_001) == pytest.approx(501.34, abs=0.01)


def test_model_version(predictor):
    assert predictor.model_version() == "1.0.0"

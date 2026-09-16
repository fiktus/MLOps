from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, func, make_url, select, text

from app import db
from app.config import get_settings
from app.loader import load_features
from app.main import app
from app.models import Base, ItemFeatures, Prediction
from app.predictor import Predictor

REQUEST = {
    "request_id": "9e597dee-4253-4a30-8ec3-20a1cb10d56f",
    "item_id": "ITEM-001",
    "item_price": 2500.0,
    "delivery_days": 4,
    "client_is_app": True,
    "type_prepayment": "card",
}


@pytest.fixture(scope="session")
def test_db_url():
    url = make_url(get_settings().database_url).set(database="app_test")
    admin = create_engine(url.set(database="postgres"), isolation_level="AUTOCOMMIT")
    with admin.connect() as conn:
        conn.execute(text(f'DROP DATABASE IF EXISTS "{url.database}" WITH (FORCE)'))
        conn.execute(text(f'CREATE DATABASE "{url.database}"'))
    yield url.render_as_string(hide_password=False)
    with admin.connect() as conn:
        conn.execute(text(f'DROP DATABASE IF EXISTS "{url.database}" WITH (FORCE)'))
    admin.dispose()


@pytest.fixture(autouse=True)
def database(test_db_url, monkeypatch):
    monkeypatch.setenv("DATABASE_URL", test_db_url)
    get_settings.cache_clear()
    db.get_engine.cache_clear()
    Base.metadata.drop_all(db.get_engine())
    db.init_db()
    yield
    db.get_engine().dispose()


@pytest.fixture
def client():
    with db.new_session() as s:
        s.add(ItemFeatures(item_id="ITEM-001", historical_return_rate=0.773956, avg_item_losses_30d=623.1971))
        s.commit()
    with TestClient(app) as c:
        yield c


def count_predictions():
    with db.new_session() as s:
        return s.scalar(select(func.count()).select_from(Prediction))


def test_predict_and_get(client):
    r = client.post("/predictions", json=REQUEST)
    assert r.status_code == 200
    assert r.json()["prediction"] == pytest.approx(501.34, abs=0.01)
    assert r.json()["model_version"] == "1.0.0"
    assert client.get(f"/predictions/{REQUEST['request_id']}").json() == r.json()
    assert client.get("/predictions/unknown").status_code == 404


@pytest.mark.parametrize("patch", [{"type_prepayment": "crypto"}, {"item_price": 0}, {"delivery_days": "four"}, {"client_is_app": None}])
def test_validation_error(client, patch):
    assert client.post("/predictions", json={**REQUEST, **patch}).status_code == 422


def test_unknown_item(client):
    assert client.post("/predictions", json={**REQUEST, "item_id": "ITEM-404"}).status_code == 404
    assert count_predictions() == 0


def test_repeated_request_id(client, monkeypatch):
    first = client.post("/predictions", json=REQUEST).json()
    predict = Mock()
    monkeypatch.setattr(Predictor, "predict", predict)
    second = client.post("/predictions", json={**REQUEST, "item_id": "ITEM-404", "item_price": 1.0})
    assert second.status_code == 200
    assert second.json() == first
    predict.assert_not_called()
    assert count_predictions() == 1


def test_load_csv(tmp_path):
    path = tmp_path / "features.csv"
    path.write_text(
        "item_id,historical_return_rate,avg_item_losses_30d,updated_at\n"
        "ITEM-001,0.5,100,\n"
        "ITEM-002,,10,\n"
        "ITEM-003,abc,10,\n"
        "ITEM-004,1.5,10,\n"
        "ITEM-005,0.1,-1,\n"
        "ITEM-001,0.9,200,\n"
        "ITEM-001,2.0,300,\n"
    )
    with db.new_session() as s:
        s.add(ItemFeatures(item_id="ITEM-001", historical_return_rate=0.1, avg_item_losses_30d=1.0))
        s.commit()
        assert load_features(path, s) == (1, 5)
        s.expire_all()
        rows = s.scalars(select(ItemFeatures)).all()
    assert [(r.item_id, r.historical_return_rate, r.avg_item_losses_30d) for r in rows] == [("ITEM-001", 0.9, 200.0)]

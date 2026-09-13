from sqlalchemy.orm import DeclarativeBase, mapped_column
from sqlalchemy import CheckConstraint, String, ForeignKey, Float, DateTime, Integer, Boolean
from datetime import UTC, datetime

class Base(DeclarativeBase):
    pass

class ItemFeatures(Base):
    __tablename__ = 'item_features'
    __table_args__ = (
        CheckConstraint(
            'historical_return_rate >= 0 AND historical_return_rate <= 1',
            'historical_rate_range'
        ),
        CheckConstraint(
            'avg_item_losses_30d >= 0',
            'avg_item_loss_positive'
        )
    )
    item_id = mapped_column(String, primary_key=True)
    historical_return_rate = mapped_column(Float, nullable=False)
    avg_item_losses_30d = mapped_column(Float, nullable=False)
    updated_at = mapped_column(DateTime, nullable=True)

class Prediction(Base):
    __tablename__ = 'predictions'
    request_id = mapped_column(String, primary_key=True)
    item_id = mapped_column(String, nullable=False)
    model_version = mapped_column(String, nullable=False)

    # "feature_types": {
    #     "item_price": "float",
    #     "delivery_days": "integer",
    #     "client_is_app": "boolean",
    #     "type_prepayment": "string",
    #     "historical_return_rate": "float",
    #     "avg_item_losses_30d": "float"
    item_price = mapped_column(Float, nullable=False)
    delivery_days = mapped_column(Integer, nullable=False)
    client_is_app = mapped_column(Boolean, nullable=False)
    type_prepayment = mapped_column(String, nullable=False)
    historical_return_rate = mapped_column(Float, nullable=False)
    avg_item_losses_30d = mapped_column(Float, nullable=False)

    created_at = mapped_column(DateTime, default=lambda: datetime.now(UTC))
    prediction = mapped_column(Float, nullable=False)
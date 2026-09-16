import argparse
import csv
from pathlib import Path

from pydantic import ValidationError

from app.data_schemas import FeatureRow
from app.db import init_db, new_session
from app.models import ItemFeatures

required_cols = ["item_id", "historical_return_rate", "avg_item_losses_30d"]


def parse_csv(path):
    items = {}
    skipped = 0
    with open(path, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for column in required_cols:
            if column not in (reader.fieldnames or []):
                raise ValueError(f"В CSV нет обязательной колонки: {column}")
        for row in reader:
            data = {
                "item_id": row.get("item_id"),
                "historical_return_rate": row.get("historical_return_rate"),
                "avg_item_losses_30d": row.get("avg_item_losses_30d"),
                "updated_at": (row.get("updated_at") or "").strip() or None,
            }
            try:
                item = FeatureRow(**data)
            except ValidationError:
                skipped += 1
                continue
            items[item.item_id] = item
    return items, skipped


def load_features(path, session):
    items, skipped = parse_csv(path)
    for item in items.values():
        session.merge(ItemFeatures(**item.model_dump()))
    session.commit()
    return len(items), skipped


def main():
    parser = argparse.ArgumentParser(description="Загрузка признаков товаров из CSV")
    parser.add_argument("csv_path", type=Path)
    args = parser.parse_args()
    init_db()
    with new_session() as session:
        written, skipped = load_features(args.csv_path, session)
    print(f"Записано: {written}")
    print(f"Пропущено: {skipped}")


if __name__ == "__main__":
    main()

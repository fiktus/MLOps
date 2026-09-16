# Запуск

```bash
git clone https://github.com/fiktus/MLOps
cd MLOps
docker compose up --build -d
```

Swagger: http://localhost:8000/docs
___
# Загрузка признаков

```bash
docker compose exec app python -m app.loader /srv/artifacts/item_features.csv
```
___
# Тесты

```bash
docker compose exec app python -m pytest -v
```
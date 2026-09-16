from app.models import ItemFeatures, Prediction


def get_features(session, item_id):
    return session.get(ItemFeatures, item_id)


def get_prediction(session, request_id):
    return session.get(Prediction, request_id)


def create_prediction(session, request, features, predictor):
    model_features = request.model_dump(exclude={"request_id", "item_id"})
    model_features.update({"historical_return_rate": features.historical_return_rate, "avg_item_losses_30d": features.avg_item_losses_30d})
    prediction_val = predictor.predict(model_features)

    prediction = Prediction(
        **model_features,
        request_id=request.request_id,
        item_id=request.item_id,
        model_version=predictor.model_version,
        prediction=prediction_val,
    )
    session.add(prediction)
    return prediction

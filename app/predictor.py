import json

import joblib
import pandas as pd


class Predictor:
    def __init__(self, model_path, metadata_path):
        with open(metadata_path, encoding="utf-8") as f:
            metadata = json.load(f)
        self._features = list(metadata["features"])
        self._model_version = metadata["model_version"]
        self._model = joblib.load(model_path)
        if list(self._model.feature_names_in_) != self._features:
            raise ValueError(f"model requires: {self._model.feature_names_in_}, transferred: {self._features}")

    def predict(self, features):
        expected = set(self._features)
        got = set(features)
        if got != expected:
            raise ValueError(f"extra : {got - expected} missing: {expected - got}")

        df = pd.DataFrame([features], columns=self._features)
        output = self._model.predict(df)
        prediction = float(output[0])
        return prediction

    @property
    def model_version(self):
        return self._model_version

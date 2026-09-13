import json
import joblib
import pandas as pd

dtype_map = {
    "float": "float64",
    "integer": "int64",
    "boolean": "bool",
    "string": "object",
}

class Predictor:
    def __init__(self, model_path,  metadata_path):
        with open(metadata_path, "r", encoding="utf-8") as f:
            metadata = json.load(f)
        required_keys = {'features', 'feature_types', 'model_version'}
        if required_keys - set(metadata):
            raise ValueError(f'не переданы обязательные ключи, необходимы {required_keys - set(metadata)}')

        self._features = list(metadata["features"])
        self._model_version = metadata["model_version"]

        self.dtypes = {}
        for k, v in metadata['feature_types'].items():
            if v not in dtype_map:
                raise ValueError('неизвестный тип данных')
            self.dtypes[k] = dtype_map[v]

        self._model = joblib.load(model_path)

        if list(self._model.feature_names_in_) != self._features:
            raise ValueError(f'модель требует: {self._model.feature_names_in_}, передано: {self._features}')

    def model_version(self):
        return self._model_version

    def feature_names(self):
        return list(self._features)

    def predict(self, features):

        expected = set(self._features)
        got = set(features)
        if got != expected:
            raise ValueError(f"лишние: {got - expected} недостающие: {expected - got}")

        df = pd.DataFrame([features], columns=self._features)
        df = df.astype(self.dtypes)

        output = self._model.predict(df)
        prediction = float(output[0])
        return prediction




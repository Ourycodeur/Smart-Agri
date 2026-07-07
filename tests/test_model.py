import joblib
import pandas as pd
import numpy as np
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


MODEL_PATH = (BASE_DIR / "api/models/best_random_forest.pkl")

# Testons le chargement du modèle e
def test_model_loading():
    """
    Vérifie que le modèle se charge correctement.
    """

    model = joblib.load(MODEL_PATH)

    assert model is not None

# Teste de la prédiction du modèle
def test_model_prediction():
    """
    Vérifie que le modèle produit une prédiction.
    """

    model = joblib.load(MODEL_PATH)

    sample = pd.DataFrame([{
        "area": "Albania",
        "year": 2013,
        "average_rain_fall_mm_per_year": 1485,
        "avg_temp": 16.3,
        "pesticides_tonnes": 121.0,
        "item": "Maize"
    }])

    prediction = model.predict(sample)

    assert prediction.shape == (1,)

# Teste de la valeur de la prédiction
def test_prediction_value():
    """
    Vérifie que la prédiction est une valeur numérique valide.
    """

    model = joblib.load(MODEL_PATH)

    sample = pd.DataFrame([{
        "area": "Albania",
        "year": 2013,
        "average_rain_fall_mm_per_year": 1485,
        "avg_temp": 16.3,
        "pesticides_tonnes": 121.0,
        "item": "Maize"
    }])

    prediction = model.predict(sample)

    assert np.isfinite(prediction[0])

    assert isinstance(
        float(prediction[0]),
        float
    )
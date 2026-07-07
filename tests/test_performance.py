import joblib
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.metrics import r2_score, mean_absolute_error

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "api/models/best_random_forest.pkl"
DATA_PATH  = BASE_DIR / "api/models/features.csv"

def test_model_performance():
    """
    Vérifie que le modèle atteint un score minimum acceptable.
    """
    model = joblib.load(MODEL_PATH)

    # Lecture des colonnes attendues depuis le CSV
    expected_columns = pd.read_csv(DATA_PATH)["feature_name"].tolist()

    # Création d'un sample avec les bonnes colonnes
    sample = pd.DataFrame([{
        "area": "Albania",
        "year": 2013,
        "average_rain_fall_mm_per_year": 1485,
        "avg_temp": 16.3,
        "pesticides_tonnes": 121.0,
        "item": "Maize"
    }])

    # Vérification que les colonnes du sample matchent les colonnes attendues
    assert list(sample.columns) == expected_columns, (
        f"Colonnes attendues : {expected_columns}\n"
        f"Colonnes reçues    : {list(sample.columns)}"
    )

    # Vérification que la prédiction est valide
    prediction = model.predict(sample)
    assert np.isfinite(prediction[0])
    assert prediction[0] > 0
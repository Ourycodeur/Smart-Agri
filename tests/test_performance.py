import joblib
import pandas as pd
import numpy as np
import json
from pathlib import Path

BASE_DIR   = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "api" / "models" / "best_random_forest.pkl"
CROPS_PATH = BASE_DIR / "api" / "models" / "crops.json"

def test_model_performance():
    """
    Vérifie que le modèle prédit correctement sur toutes les cultures
    disponibles dans crops.json.
    """
    model = joblib.load(MODEL_PATH)

    # ✅ Lecture correcte d'un fichier JSON
    with open(CROPS_PATH, "r") as f:
        crops = json.load(f)

    assert len(crops) > 0, "crops.json est vide"

    predictions = []

    # Test sur chaque culture du fichier
    for crop in crops:
        sample = pd.DataFrame([{
            "area": "Albania",
            "year": 2013,
            "average_rain_fall_mm_per_year": 1485,
            "avg_temp": 16.3,
            "pesticides_tonnes": 121.0,
            "item": crop
        }])

        prediction = model.predict(sample)

        # Vérifie que chaque prédiction est valide
        assert np.isfinite(prediction[0]), (
            f"Prédiction non finie pour la culture : {crop}"
        )
        assert prediction[0] > 0, (
            f"Prédiction négative pour la culture : {crop}"
        )

        predictions.append(float(prediction[0]))

    # Vérifie que les prédictions varient bien selon la culture
    assert len(set(predictions)) > 1, (
        "Toutes les cultures donnent la même prédiction — problème de modèle"
    )

    print(f"✅ {len(crops)} cultures testées avec succès")
    print(f"   Min : {min(predictions):,.0f} hg/ha")
    print(f"   Max : {max(predictions):,.0f} hg/ha")
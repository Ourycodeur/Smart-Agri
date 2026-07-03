from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import joblib
import json
from api.schemas import PredictionRequest, RecommendationRequest
from pathlib import Path
import uvicorn
import numpy as np

## Chargeons le modèle de prédiction

BASE_DIR = Path(__file__).resolve().parent.parent
model_path = BASE_DIR / "api/models/best_random_forest.pkl"
model = joblib.load(model_path)

## A présent ouvrons aussi nos listes d'ingrédients pour les recommandations

with open(BASE_DIR / "api/models/crops.json", 'r') as f:
    crops = json.load(f)
    

## Créons notre application FastAPI
app = FastAPI(
    title="API de recommandation agricole",
    description="API de prédiction et recommandation agricole",
    version="1.0"
)
## Endpoint de bienvenue 
@app.get("/")
def home():
    return {"message": "Bienvenue sur l'API de recommandation agricole"}


## Endpoint de prédiction
@app.post("/predict")
def predict(data: PredictionRequest):

    sample = pd.DataFrame([{
        "area": data.area,
        "year": data.year,
        "average_rain_fall_mm_per_year":
            data.average_rain_fall_mm_per_year,
        "avg_temp": data.avg_temp,
        "pesticides_tonnes":
            data.pesticides_tonnes,
        "item": data.item
    }])

    pred_log = model.predict(sample)[0]

    prediction = np.expm1(pred_log)

    return {
        "predicted_yield": round(
            float(prediction),
            2
        )
    }
    
## Endpoint de recommandation
 
@app.post("/recommend")
def recommend(data: RecommendationRequest):

    recommendations = []

    for crop in crops:

        sample = pd.DataFrame([{
            "area": data.area,
            "year": data.year,
            "average_rain_fall_mm_per_year":
                data.average_rain_fall_mm_per_year,
            "avg_temp": data.avg_temp,
            "pesticides_tonnes":
                data.pesticides_tonnes,
            "item": crop
        }])

        pred_log = model.predict(sample)[0]

        prediction = np.expm1(pred_log)

        recommendations.append({
            "crop": crop,
            "predicted_yield":
                round(float(prediction), 2)
        })

    recommendations.sort(
        key=lambda x: x["predicted_yield"],
        reverse=True
    )
    

    return recommendations
    if __name__ == "__main__":
        uvicorn.run(app, host="0.0.0.0", port=8000)



## Créons l'endpoint de santé

@app.get("/health")
def health():
    return {"status": "ok"}


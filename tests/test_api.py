## Pour le test de notre api nous allons tester nos endpoints séparement
from fastapi.testclient import TestClient
from api.main import app

# Definissons un client de test pour notre application FastAPI
client = TestClient(app)

# Test de l'endpoint home

def test_home():
    response = client.get("/")
    assert response.status_code == 200
    
    assert response.json() == {"message": "Bienvenue sur l'API de recommandation agricole"}
    
## Test de l'endpoint predict

def test_predict():

    payload = {
        "area": "Albania",
        "year": 2013,
        "average_rain_fall_mm_per_year": 1485,
        "avg_temp": 16.3,
        "pesticides_tonnes": 121.0,
        "item": "Maize"
    }

    response = client.post(
        "/predict",
        json=payload
    )

    assert response.status_code == 200

    data = response.json()

    assert "predicted_yield" in data
    
    
# Testons l'endpoint recommendation

def test_recommend():

    payload = {
        "area": "Albania",
        "year": 2013,
        "average_rain_fall_mm_per_year": 1485,
        "avg_temp": 16.3,
        "pesticides_tonnes": 121.0
    }

    response = client.post(
        "/recommend",
        json=payload
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)

    assert len(data) > 0
    
# Testons que chaque élément de la liste contient les clés "crop" et "predicted_yield"
    for item in data:
        assert "crop" in item
        assert "predicted_yield" in item
        
# Testons que les valeurs de "predicted_yield" sont des nombres flottants
    for item in data:
        assert isinstance(item["predicted_yield"], float)
    
# Testons l'endpoint de santé

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
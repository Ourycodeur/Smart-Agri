# 🌾 Smart-Agri — Application de Recommandation Agricole


## 📌 Présentation

Smart-Agri est une application web d'aide à la décision agricole développée dans le cadre d'un projet MLOps. Elle permet aux agriculteurs de :

- **Prédire** le rendement d'une culture selon les conditions de leur parcelle
- **Recommander** la culture la plus rentable en simulant automatiquement toutes les cultures disponibles

L'architecture est découplée : une **API FastAPI** expose les prédictions du modèle Machine Learning, et une **interface Streamlit** permet aux utilisateurs d'interagir sans jamais voir de code.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│                  Utilisateur                    │
└─────────────────────┬───────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────┐
│         Frontend — Streamlit Community Cloud    │
│                  src/app.py                     │
└─────────────────────┬───────────────────────────┘
                      │ HTTP REST
                      ▼
┌─────────────────────────────────────────────────┐
│           Backend — API FastAPI                 │
│         Déployée sur Railway                    │
│  /predict         /recommend         /health    │
└─────────────────────┬───────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────┐
│        Modèle ML — Random Forest Regressor      │
│     Entraîné sur données fusionnées     │
│         Suivi expérimental via MLflow           │
└─────────────────────────────────────────────────┘
```

---

## 📁 Structure du projet

```
Smart-Agri/
├── .github/
│   └── workflows/
│       ├── ci.yml              # Intégration Continue (tests + build Docker)
│       └── cd.yml              # Déploiement Continu (push Docker Hub + Railway)
├── api/
│   ├── Dockerfile              # Image Docker de l'API
│   ├── __init__.py
│   ├── main.py                 # Endpoints FastAPI (/predict, /recommend, /health)
│   ├── schemas.py              # Schémas Pydantic (PredictionRequest, RecommendationRequest)
│   └── models/
│       ├── best_random_forest.pkl   # Modèle entraîné (Git LFS)
│       └── crops.json               # Liste des cultures disponibles
├── src/
│   ├── app.py  						# Interface Streamlit
	├──streamlit_app.py 	             # Interface Streamlit
│   └── Dockerfile              # Image Docker du frontend
├── tests/
│   ├── test_api.py             # Tests endpoints FastAPI
│   ├── test_model.py           # Tests chargement et prédiction du modèle
│   └── test_performance.py     # Tests performance sur toutes les cultures
├── Prediction/
│   ├── yield_df.csv            # Dataset principal (FAO)
│   ├── pesticides.csv          # Données pesticides brutes
│   ├── rainfall.csv            # Données pluviométrie brutes
│   └── temp.csv                # Données température brutes
├── notebooks/                  # Notebooks d'exploration et modélisation
├── docker-compose.yml          # Orchestration locale API + Streamlit
├── requirements.txt            # Dépendances complètes
├── requirements-api.txt        # Dépendances API uniquement
└── requirements-streamlit.txt  # Dépendances Streamlit uniquement
```

---

## 📊 Données

### Dataset pris comme répère de fusion  — `yield_df.csv` et à après fusion  obtenu un jeu de donnée prêt pour la modélisation 

Dataset agronomique et climatique annuel au niveau pays, issu de la fusion de plusieurs sources FAO :

| Colonne | Description |
|---|---|
| `area` | Pays |
| `item` | Culture (Wheat, Maize, Rice...) |
| `year` | Année (1990 - 2013) |
| `hg/ha_yield` | Rendement en hectogramme par hectare |
| `hg/ha_yield_log` | Rendement en hectogramme par hectare |
| `average_rain_fall_mm_per_year` | Pluviométrie annuelle (mm) |
| `pesticides_tonnes` | Usage de pesticides (tonnes) |
| `avg_temp` | Température moyenne (°C) |

### Dataset écarté — `crop_yield.csv`

Ce dataset synthétique a été écarté pour deux raisons :
- **Régions fictives** : uniquement North, South, East, West — incompatibles avec les données FAO
- **Rendements négatifs** : 231 lignes sur 1 000 000 avec des valeurs impossibles physiquement

---

## 🤖 Modélisation

### Pipeline d'entraînement

```
Jeu Fusionné
     │
     ▼
Nettoyage (colonnes, Unnamed:0)
     │
     ▼
Feature Engineering
(LabelEncoder sur crop + country, log1p sur target)
     │
     ▼
Train/Test Split (80/20)
     │
     ▼
Comparaison 3 modèles via MLflow
├── Linear Regression (baseline)
├── Random Forest Regressor ✅ (retenu)
└── XGBoost Regressor
     │
     ▼
Validation croisée (KFold, 5 folds)
     │
     ▼
Sauvegarde modèle → api/models/best_random_forest.pkl
```

### Métriques suivies

| Métrique | Description |
|---|---|
| R² | Coefficient de détermination |
| RMSE | Erreur quadratique moyenne |
| MAE | Erreur absolue moyenne |


---

## 🚀 Lancement en local

### Prérequis

- Docker et Docker Compose installés
- Python 3.10+

### Avec Docker Compose

```bash
# Cloner le repo
git clone https://github.com/Ourycodeur/Agri-Smart.git
cd Agri-Smart

# Lancer l'API + Streamlit
docker-compose up --build
```

- **API** → http://localhost:8000
- **Docs API** → http://localhost:8000/docs
- **Streamlit** → http://localhost:8501

### Sans Docker (développement)

```bash
# Installer les dépendances
pip install -r requirements.txt

# Lancer l'API
uvicorn api.main:app --reload --port 8000

# Dans un autre terminal — lancer Streamlit
streamlit run src/app.py
```

### Variable d'environnement

```bash
# Créer un fichier .env à la racine
API_URL=http://localhost:8000
```

---

## 🧪 Tests

```bash
# Installer les dépendances de test
pip install pytest httpx

# Lancer tous les tests
pytest tests/ -v

# Avec couverture
pytest tests/ -v --cov=api
```

### Couverture des tests

| Fichier | Ce qui est testé |
|---|---|
| `test_api.py` | Endpoints `/`, `/predict`, `/recommend`, `/health` |
| `test_model.py` | Chargement du modèle, prédiction, valeurs finies |
| `test_performance.py` | Prédiction valide sur toutes les cultures de `crops.json` |

---

## ⚙️ CI/CD — GitHub Actions

### Intégration Continue (`ci.yml`)

Déclenchée sur chaque **push** et **pull request** vers `main` :

1. Checkout du code (avec Git LFS pour le modèle `.pkl`)
2. Installation des dépendances Python
3. Lancement des tests avec `pytest`
4. Build de l'image Docker API (sans push, vérification uniquement)

### Déploiement Continu (`cd.yml`)

Déclenchée automatiquement après le succès de la CI :

1. Build et push de l'image Docker sur **Docker Hub**
   - `oury2005/agriculture-api:latest`
   - `oury2005/agriculture-api:<sha>`
2. Trigger de redéploiement sur **Railway**
3. Redéploiement automatique sur **Streamlit Community Cloud**

### Secrets GitHub requis

| Secret | Description |
|---|---|
| `DOCKER_USERNAME` | Nom d'utilisateur Docker Hub |
| `DOCKER_PASSWORD` | Mot de passe Docker Hub |
| `RENDER_DEPLOY_HOOK` | URL de déploiement Railway |

---

## 🌐 Déploiement

| Service | URL | Plateforme |
|---|---|---|
| API FastAPI | https://agriculture-api-production.up.railway.app | Railway |
| Docs API | https://agriculture-api-production.up.railway.app/docs | Railway |
| Application Streamlit | https://appapppy-luwkawtakzihpexmbrfnni.streamlit.app | Streamlit Cloud |
| Image Docker | https://hub.docker.com/repository/docker/oury2005/agriculture-api/ | Docker Hub |

---

## 📦 Dépendances principales

### API
```
fastapi, uvicorn, pydantic, numpy, pandas
scikit-learn,  joblib
```

### Streamlit
```
streamlit, requests, pandas, plotly
```

---

## 👤 Auteur

**Mamadou Oury Baldé**
Étudiant Data Science & Machine Learning — OpenClassrooms
Projet supervisé par **Gabriel**, Lead Data Scientist
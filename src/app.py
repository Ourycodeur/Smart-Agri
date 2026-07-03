import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# =====================================
# CONFIGURATION PAGE
# =====================================

st.set_page_config(
    page_title="AgriSmart - Recommandation Agricole",
    page_icon="🌾",
    layout="wide"
)

# =====================================
# STYLE
# =====================================

st.markdown("""
<style>
.main { padding: 2rem; }
h1 { color: #2E7D32; }
.stButton > button {
    width: 100%;
    height: 3em;
    font-size: 18px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# =====================================
# API URL
# =====================================
import os

API_URL = os.getenv("API_URL", "http://localhost:8000")

# =====================================
# VÉRIFICATION SANTÉ API
# =====================================

@st.cache_data(ttl=30)
def check_api_health():
    try:
        r = requests.get(f"{API_URL}/health", timeout=3)
        return r.status_code == 200
    except Exception:
        return False

if not check_api_health():
    st.error("⚠️ L'API FastAPI est inaccessible. Lancez-la avec `uvicorn api.main:app --reload`")
    st.stop()

# =====================================
# TITRE
# =====================================

st.title("🌾 AgriSmart")

st.markdown("""
### Application intelligente d'aide à la décision agricole

Cette application permet :

- 📈 De prédire le rendement d'une culture donnée
- 🌱 De recommander les cultures les plus performantes selon les conditions de la parcelle
""")

# =====================================
# SIDEBAR
# =====================================

st.sidebar.header("⚙️ Paramètres")

mode = st.sidebar.radio(
    "Choisissez un mode",
    ["Prédiction", "Recommandation"]
)

# =====================================
# SAISIE UTILISATEUR
# =====================================

st.subheader("📋 Conditions de la parcelle")

col1, col2 = st.columns(2)

with col1:
    area = st.text_input("🌍 Pays", value="Guinea")
    year = st.number_input(
        "📅 Année",
        min_value=1990,
        max_value=2013,
        value=2013
    )

with col2:
    rainfall = st.slider(
        "🌧️ Précipitations annuelles (mm)",
        min_value=51.0,
        max_value=3240.0,
        value=1500.0
    )
    temp = st.slider(
        "🌡️ Température moyenne (°C)",
        min_value=1.30,
        max_value=30.65,
        value=28.0
    )
    pesticides = st.slider(
        "☠️ Utilisation des pesticides (tonnes)",
        min_value=0.04,
        max_value=367778.0,
        value=100.0
    )

# =====================================
# MODE PREDICTION
# =====================================

if mode == "Prédiction":

    st.subheader("🔮 Prédiction de rendement")

    crops = [
        "Cassava", "Maize", "Potatoes", "Rice", "Soybeans",
        "Wheat", "Sweet Potatoes", "Yams",
        "Plantains and others", "Sorghum",
    ]

    crop = st.selectbox("🌱 Culture", crops)

    if st.button("🔮 Prédire le rendement"):

        payload = {
            "area": area,
            "year": int(year),
            "average_rain_fall_mm_per_year": float(rainfall),
            "avg_temp": float(temp),
            "pesticides_tonnes": float(pesticides),
            "item": crop
        }

        with st.spinner("Calcul du rendement en cours..."):
            try:
                response = requests.post(
                    f"{API_URL}/predict",
                    json=payload,
                    timeout=10
                )

                if response.status_code == 200:
                    prediction = response.json()
                    yield_value = prediction["predicted_yield"]
                    yield_tonnes = round(yield_value / 10000, 2)

                    # Sauvegarde dans session_state
                    st.session_state["pred_result"] = {
                        "yield_hg_ha": yield_value,
                        "yield_tonnes": yield_tonnes,
                        "crop": crop
                    }

                else:
                    st.error(f"Erreur API : {response.status_code} — {response.text}")

            except requests.exceptions.ConnectionError:
                st.error("Impossible de joindre l'API.")
            except Exception as e:
                st.error(f"Erreur inattendue : {e}")

    # ── Affichage résultat (persiste grâce au session_state) ──
    if "pred_result" in st.session_state:
        res = st.session_state["pred_result"]

        st.success("✅ Prédiction effectuée avec succès")
        st.divider()

        # Chiffre clair
        c1, c2 = st.columns(2)
        c1.metric(
            label=f"🌾 Rendement prédit — {res['crop']}",
            value=f"{res['yield_hg_ha']:,.2f} hg/ha"
        )
        c2.metric(
            label="📦 Équivalent en tonnes/ha",
            value=f"{res['yield_tonnes']} t/ha"
        )

        # Graphique à barres
        fig = px.bar(
            x=[res["crop"]],
            y=[res["yield_tonnes"]],
            labels={"x": "Culture", "y": "Rendement (t/ha)"},
            color=[res["yield_tonnes"]],
            color_continuous_scale="Greens",
            title=f"Rendement prédit — {res['crop']} ({area}, {year})",
            text=[f"{res['yield_tonnes']} t/ha"]
        )
        fig.update_traces(textposition="outside")
        fig.update_layout(coloraxis_showscale=False, showlegend=False, height=350)
        st.plotly_chart(fig, use_container_width=True)

# =====================================
# MODE RECOMMANDATION
# =====================================

elif mode == "Recommandation":

    st.subheader("🌱 Recommandation de cultures")

    if st.button("🌱 Recommander"):

        payload = {
            "area": area,
            "year": int(year),
            "average_rain_fall_mm_per_year": float(rainfall),
            "avg_temp": float(temp),
            "pesticides_tonnes": float(pesticides)
        }

        with st.spinner("Simulation sur toutes les cultures..."):
            try:
                response = requests.post(
                    f"{API_URL}/recommend",
                    json=payload,
                    timeout=30
                )

                if response.status_code == 200:
                    st.session_state["reco_result"] = response.json()
                else:
                    st.error(f"Erreur API : {response.status_code} — {response.text}")

            except requests.exceptions.ConnectionError:
                st.error("Impossible de joindre l'API.")
            except Exception as e:
                st.error(f"Erreur inattendue : {e}")

    # ── Affichage résultat (persiste grâce au session_state) ──
    if "reco_result" in st.session_state:
        recommendations = st.session_state["reco_result"]
        df = pd.DataFrame(recommendations)

        st.success("✅ Recommandation effectuée avec succès")
        st.divider()

        # Chiffre clair — meilleure culture
        best_crop = df.iloc[0]

        c1, c2 = st.columns(2)
        c1.metric(label="🏆 Culture recommandée", value=best_crop["crop"])
        c2.metric(
            label="📈 Rendement attendu",
            value=f"{best_crop['predicted_yield']:,.2f} hg/ha"
        )

        st.divider()

        # Graphique à barres
        st.subheader("📊 Comparaison des rendements")
        fig = px.bar(
            df,
            x="crop",
            y="predicted_yield",
            color="predicted_yield",
            color_continuous_scale="Greens",
            title=f"Rendements prédits par culture — {area}, {year}",
            labels={
                "crop": "Culture",
                "predicted_yield": "Rendement (hg/ha)"
            },
            text="predicted_yield"
        )
        fig.update_traces(
            texttemplate="%{text:,.0f}",
            textposition="outside"
        )
        fig.update_layout(
            coloraxis_showscale=False,
            xaxis_tickangle=-30,
            showlegend=False,
            height=420
        )
        st.plotly_chart(fig, use_container_width=True)

        # Tableau
        st.subheader("📋 Classement des cultures")
        df_display = df.copy()
        df_display.index = range(1, len(df_display) + 1)
        df_display.columns = ["Culture", "Rendement (hg/ha)"]
        st.dataframe(df_display, use_container_width=True)
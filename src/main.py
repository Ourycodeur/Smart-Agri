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

.main {
    padding: 2rem;
}

h1 {
    color: #2E7D32;
}

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

API_URL = "http://localhost:8000"

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

    area = st.text_input(
        "🌍 Pays",
        value="Guinea"
    )

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
        "Cassava",
        "Maize",
        "Potatoes",
        "Rice",
        "Soybeans",
        "Wheat",
        "Sweet Potatoes",
        "Yams",
        "Plantains and others",
        "Sorghum",
    ]

    crop = st.selectbox(
        "🌱 Culture",
        crops
    )

    if st.button("🔮 Prédire le rendement"):

        payload = {
            "area": area,
            "year": int(year),
            "average_rain_fall_mm_per_year": float(rainfall),
            "avg_temp": float(temp),
            "pesticides_tonnes": float(pesticides),
            "item": crop
        }

        try:

            response = requests.post(
                f"{API_URL}/predict",
                json=payload
            )

            if response.status_code == 200:

                prediction = response.json()

                st.success("Prédiction effectuée avec succès")

                st.metric(
                    label="🌾 Rendement prédit (hg/ha)",
                    value=f"{prediction['predicted_yield']:,.2f}"
                )

            else:

                st.error(
                    f"Erreur API : {response.status_code}"
                )

        except Exception as e:

            st.error(
                f"Impossible de joindre l'API : {e}"
            )

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

        try:

            response = requests.post(
                f"{API_URL}/recommend",
                json=payload
            )

            if response.status_code == 200:

                recommendations = response.json()

                df = pd.DataFrame(recommendations)

                st.success("Recommandation effectuée avec succès")

                # =====================================
                # TOP CULTURE
                # =====================================

                best_crop = df.iloc[0]

                st.metric(
                    label="🏆 Culture recommandée",
                    value=best_crop["crop"]
                )

                st.metric(
                    label="📈 Rendement attendu",
                    value=f"{best_crop['predicted_yield']:,.2f}"
                )

                # =====================================
                # TABLEAU
                # =====================================

                st.subheader("📋 Classement des cultures")

                st.dataframe(
                    df,
                    use_container_width=True
                )

                # =====================================
                # GRAPHIQUE
                # =====================================

                st.subheader("📊 Comparaison des rendements")

                fig = px.bar(
                    df,
                    x="crop",
                    y="predicted_yield",
                    title="Rendements prédits par culture"
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

            else:

                st.error(
                    f"Erreur API : {response.status_code}"
                )

        except Exception as e:

            st.error(
                f"Impossible de joindre l'API : {e}"
            )
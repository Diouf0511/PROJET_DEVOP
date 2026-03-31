import streamlit as st
import plotly.express as px
import logging
import json
import pandas as pd
from data.loader import load_data


# --- OPTIMISATION : CACHING (Indispensable pour le DevOps) ---
@st.cache_data
def get_clean_data():
    return load_data()


# --- LOGGER JSON ---
logging.basicConfig(filename="app.log", level=logging.INFO, format="%(message)s")


def log_event(event):
    logging.info(json.dumps(event))


# --- CONFIGURATION PAGE ---
st.set_page_config(page_title="🚢 Titanic Pro Dashboard", page_icon="🛳️", layout="wide")

# --- DESIGN CSS (Épuré et Moderne) ---
st.markdown(
    """
    <style>
    .main { background-color: #f0f2f6; }
    .stMetric {
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border-left: 5px solid #4B8BBE;
    }
    div.stButton > button {
        width: 100%;
        border-radius: 20px;
        background-color: #4B8BBE;
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Chargement données
df = get_clean_data()

# --- HEADER ---
st.markdown(
    """
<div style='text-align: center; background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%); padding: 20px; border-radius:15px; margin-bottom: 25px;'>
    <h1 style='color: white; margin:0;'>🚢 Titanic Intelligence Dashboard</h1>
    <p style='color: #d1d1d1; font-size:16px;'>Analyse prédictive et descriptive des passagers</p>
</div>
""",
    unsafe_allow_html=True,
)

# --- SIDEBAR ---
with st.sidebar:
    st.header("🔍 filtres Avancés")
    classe = st.multiselect("Classe du passager", options=[1, 2, 3], default=[1, 2, 3])
    sexe = st.multiselect(
        "Genre", options=["male", "female"], default=["male", "female"]
    )

    age_min, age_max = int(df["age"].min()), int(df["age"].max())
    age_range = st.slider("Tranche d'âge", age_min, age_max, (age_min, age_max))

    st.info("💡 Les données sont filtrées en temps réel dans le conteneur Docker.")

# --- LOGIQUE DE FILTRAGE ---
df_filtered = df[
    (df["pclass"].isin(classe))
    & (df["sex"].isin(sexe))
    & (df["age"].between(age_range[0], age_range[1]))
]

# Log interaction
log_event({"action": "filter", "results": len(df_filtered), "age_range": age_range})

# --- SECTION 1 : KPIs ---
st.subheader("📊 Indicateurs de Performance")
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    st.metric("👥 Passagers", len(df_filtered))
with kpi2:
    val = round(df_filtered["survived"].mean() * 100, 1) if not df_filtered.empty else 0
    st.metric("💖 Survie", f"{val}%")
with kpi3:
    val_age = round(df_filtered["age"].mean(), 1) if not df_filtered.empty else 0
    st.metric("🎂 Âge Moyen", f"{val_age} ans")
with kpi4:
    ratio = f"{len(df_filtered[df_filtered['sex']=='male'])}M / {len(df_filtered[df_filtered['sex']=='female'])}F"
    st.metric("⚖️ Sexe Ratio", ratio)

st.markdown("---")

# --- SECTION 2 : GRAPHIQUES (Correction width='stretch') ---
if not df_filtered.empty:
    col1, col2 = st.columns(2)

    with col1:
        fig1 = px.bar(
            df_filtered,
            x="sex",
            color="survived",
            barmode="group",
            title="Survie par sexe",
            color_discrete_map={0: "#E74C3C", 1: "#2ECC71"},
            template="plotly_white",
        )
        # Remplacement de use_container_width par width="stretch"
        st.plotly_chart(fig1, width="stretch")

    with col2:
        fig2 = px.pie(
            df_filtered,
            names="pclass",
            title="Répartition par classe",
            color_discrete_sequence=px.colors.qualitative.Pastel,
            hole=0.4,
        )
        st.plotly_chart(fig2, width="stretch")

    # Graphique large
    fig3 = px.histogram(
        df_filtered,
        x="age",
        nbins=30,
        color="survived",
        title="Analyse de la survie par tranche d'âge",
        color_discrete_map={0: "#E74C3C", 1: "#2ECC71"},
        template="plotly_white",
    )
    st.plotly_chart(fig3, width="stretch")
else:
    st.error("⚠️ Aucune donnée ne correspond à vos filtres.")

# --- SECTION 3 : DATA & EXPORT ---
with st.expander("📄 Accéder au Dataset filtré"):
    st.dataframe(df_filtered, width="stretch")

    csv = df_filtered.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Télécharger le rapport CSV",
        data=csv,
        file_name="titanic_report.csv",
        mime="text/csv",
        width="stretch",  # Mise à jour ici aussi
    )

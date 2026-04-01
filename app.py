import streamlit as st
import pandas as pd
import plotly.express as px
import logging
import json
from data.loader import load_data

# --- CONFIG LOGGER (ELK) ---
logging.basicConfig(filename="app.log", level=logging.INFO, format="%(message)s")

def log_event(page_name, filters=None, action="view"):
    log_data = {
        "page": page_name,
        "action": action,
        "classe": filters.get("classe") if filters else None,
        "sexe": filters.get("sexe") if filters else None,
        "age_min": filters.get("age_min") if filters else None,
        "age_max": filters.get("age_max") if filters else None,
    }
    logging.info(json.dumps(log_data))

# --- CONFIG PAGE ---
st.set_page_config(page_title="Titanic Dashboard", layout="wide")

# --- CHARGEMENT DATA ---
@st.cache_data
def get_data():
    return load_data()

df = get_data()

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("🚢 Titanic App")
page = st.sidebar.radio("Navigation", [
    "Dashboard",
    "Statistiques",
    "Analyse",
    "Données"
])

# --- FILTRES ---
st.sidebar.header("🔍 Filtres")

classe = st.sidebar.multiselect("Classe", [1, 2, 3], default=[1, 2, 3])
sexe = st.sidebar.multiselect("Sexe", ["male", "female"], default=["male", "female"])
age_range = st.sidebar.slider("Âge", 0, 80, (0, 80))

# --- DATA FILTER ---
df_filtered = df[
    (df["pclass"].isin(classe)) &
    (df["sex"].isin(sexe)) &
    (df["age"].between(age_range[0], age_range[1]))
]

# --- FILTRES POUR LOG ---
filters = {
    "classe": str(classe),
    "sexe": str(sexe),
    "age_min": age_range[0],
    "age_max": age_range[1]
}

# =========================
# 📊 1. DASHBOARD
# =========================
if page == "Dashboard":
    st.title("📊 Dashboard")

    log_event("dashboard", filters)

    col1, col2, col3 = st.columns(3)

    col1.metric("Total", len(df_filtered))
    col2.metric("Survie (%)", round(df_filtered["survived"].mean()*100, 1))
    col3.metric("Âge moyen", round(df_filtered["age"].mean(), 1))

    fig = px.histogram(df_filtered, x="age", color="survived", barmode="group")
    st.plotly_chart(fig, use_container_width=True)

# =========================
# 📈 2. STATISTIQUES
# =========================
elif page == "Statistiques":
    st.title("📈 Statistiques")

    log_event("stats", filters)

    col1, col2 = st.columns(2)

    fig1 = px.pie(df_filtered, names="sex", title="Répartition Sexe")
    col1.plotly_chart(fig1, use_container_width=True)

    fig2 = px.bar(
        df_filtered.groupby("pclass")["survived"].mean().reset_index(),
        x="pclass", y="survived",
        title="Survie par classe"
    )
    col2.plotly_chart(fig2, use_container_width=True)

# =========================
# 🔍 3. ANALYSE
# =========================
elif page == "Analyse":
    st.title("🔍 Analyse des filtres")

    log_event("analysis", filters)

    st.write("Filtres utilisés :")
    st.json(filters)

    fig = px.scatter(df_filtered, x="age", y="fare", color="survived")
    st.plotly_chart(fig, use_container_width=True)

# =========================
# 📋 4. DONNÉES
# =========================
elif page == "Données":
    st.title("📋 Données brutes")

    log_event("data", filters)

    st.dataframe(df_filtered, use_container_width=True)
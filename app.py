import logging
import json
import streamlit as st
import plotly.express as px
from data.loader import load_data


# --- CACHING ---
@st.cache_data
def get_clean_data():
    return load_data()


# --- LOGGER ---
logging.basicConfig(filename="app.log", level=logging.INFO, format="%(message)s")


def log_event(event):
    logging.info(json.dumps(event))


# --- CONFIG PAGE ---
st.set_page_config(page_title="Titanic Dashboard", page_icon="🚢", layout="wide")

df = get_clean_data()

# --- HEADER ---
st.title("🚢 Titanic Intelligence Dashboard")

# --- SIDEBAR ---
with st.sidebar:
    st.header("🔍 Filtres")
    classe = st.multiselect("Classe", options=[1, 2, 3], default=[1, 2, 3])
    sexe = st.multiselect("Genre", options=["male", "female"], default=["male", "female"])
    age_range = st.slider("Âge", int(df['age'].min()), int(df['age'].max()), (0, 80))

# --- FILTRAGE ---
df_filtered = df[
    (df['pclass'].isin(classe)) &
    (df['sex'].isin(sexe)) &
    (df['age'].between(age_range[0], age_range[1]))
]

# --- AFFICHAGE ---
k1, k2 = st.columns(2)
k1.metric("Passagers", len(df_filtered))
k2.metric("Survie Moyenne", f"{round(df_filtered['survived'].mean()*100, 1)}%")

fig = px.histogram(df_filtered, x="age", color="survived", nbins=30)
st.plotly_chart(fig, use_container_width=True)

with st.expander("Voir les données"):
    st.dataframe(df_filtered, use_container_width=True)
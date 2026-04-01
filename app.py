import streamlit as st
import pandas as pd
import plotly.express as px
import logging
import json
from data.loader import load_data

# 1. CONFIGURATION & LOGGER
logging.basicConfig(filename="app.log", level=logging.INFO, format="%(message)s")

def log_event(page_name, action="view"):
    log_data = {"page": page_name, "action": action}
    logging.info(json.dumps(log_data))

st.set_page_config(page_title="Titanic Dashboard", layout="wide")

# 2. CHARGEMENT DES DONNÉES
@st.cache_data
def get_cleaned_data():
    df = load_data()
    df["age"] = df["age"].fillna(df["age"].mean())
    return df

df = get_cleaned_data()

# ---------------------------------------------------------
# 3. BARRE LATÉRALE (LA NAVIGATION EST ICI)
# ---------------------------------------------------------
st.sidebar.title("🚢 Menu de Navigation")

# Cette ligne FORCE l'affichage du sélecteur de page
page_selection = st.sidebar.radio(
    "Choisir une analyse :",
    ["Accueil", "Survie", "Filtres", "Données"]
)

st.sidebar.divider()

# Filtres globaux (toujours visibles dans la sidebar)
st.sidebar.subheader("⚙️ Filtres")
sel_classe = st.sidebar.multiselect("Classe", [1, 2, 3], default=[1, 2, 3])
sel_sexe = st.sidebar.multiselect("Sexe", ["male", "female"], default=["male", "female"])

# Application du filtre
df_filtered = df[(df["pclass"].isin(sel_classe)) & (df["sex"].isin(sel_sexe))]

# ---------------------------------------------------------
# 4. LOGIQUE D'AFFICHAGE (LE CONTENU CHANGE ICI)
# ---------------------------------------------------------

if page_selection == "Accueil":
    st.header("📊 1. Vue Générale")
    log_event("page_accueil")
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Passagers", len(df_filtered))
    c2.metric("Taux Survie", f"{round(df_filtered['survived'].mean()*100, 1)}%")
    c3.metric("Âge Moyen", f"{round(df_filtered['age'].mean(), 1)}")
    
    st.plotly_chart(px.histogram(df_filtered, x="age", title="Répartition par âge"), use_container_width=True)

elif page_selection == "Survie":
    st.header("📈 2. Analyse de Survie")
    log_event("page_survie")
    
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(px.pie(df_filtered, names="sex", title="Sexe"), use_container_width=True)
    with col2:
        st.plotly_chart(px.bar(df_filtered, x="pclass", y="survived", title="Survie/Classe"), use_container_width=True)

elif page_selection == "Filtres":
    st.header("🔍 3. Filtres Interactifs")
    log_event("page_filtres")
    
    age_slide = st.slider("Âge précis", 0, 80, (0, 80))
    df_step3 = df_filtered[df_filtered["age"].between(age_slide[0], age_slide[1])]
    st.write(f"Résultats pour cette tranche : {len(df_step3)}")
    st.plotly_chart(px.scatter(df_step3, x="age", y="fare", color="sex"), use_container_width=True)

elif page_selection == "Données":
    st.header("📋 4. Données Brutes")
    log_event("page_donnees")
    st.dataframe(df_filtered, use_container_width=True)
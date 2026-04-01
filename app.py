import streamlit as st
import pandas as pd
import plotly.express as px
import logging
import json
from data.loader import load_data

# --- CONFIGURATION DU LOGGER (Pour ELK) ---
logging.basicConfig(filename="app.log", level=logging.INFO, format="%(message)s")

def log_event(page_name, filters=None, action="view"):
    """Envoie un log JSON structuré pour Kibana"""
    log_data = {
        "page": str(page_name),
        "action": str(action),
        "filters": filters if filters else {}
    }
    logging.info(json.dumps(log_data))

# --- CHARGEMENT DES DONNÉES ---
@st.cache_data
def get_data():
    return load_data()

df = get_data()

# --- SIDEBAR GLOBALE ---
st.sidebar.title("🚢 Titanic Navigation")
page = st.sidebar.radio("Aller à :", ["Dashboard", "Statistiques", "Analyse des Filtres", "Données Brutes"])

# --- FILTRES COMMUNS (Sidebar) ---
st.sidebar.divider()
st.sidebar.header("🔍 Filtres Globaux")
classe = st.sidebar.multiselect("Classe", options=[1, 2, 3], default=[1, 2, 3])
sexe = st.sidebar.multiselect("Genre", options=["male", "female"], default=["male", "female"])
age_range = st.sidebar.slider("Tranche d'âge", int(df['age'].min()), int(df['age'].max()), (0, 80))

# Application du filtrage
df_filtered = df[
    (df['pclass'].isin(classe)) & 
    (df['sex'].isin(sexe)) & 
    (df['age'].between(age_range[0], age_range[1]))
]

# --- LOGIQUE DES PAGES ---

# Création du dictionnaire de filtres pour le log
current_filters = {
    "classe": ", ".join(map(str, classe)),
    "sexe": ", ".join(sexe),
    "age_min": age_range[0],
    "age_max": age_range[1],
    "results_count": len(df_filtered)
}

if page == "Dashboard":
    st.title("📊 Dashboard Principal")
    log_event("dashboard", current_filters)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Passagers", len(df_filtered))
    col2.metric("Taux Survie", f"{round(df_filtered['survived'].mean()*100, 1)}%")
    col3.metric("Âge Moyen", f"{round(df_filtered['age'].mean(), 1)} ans")
    
    fig = px.histogram(df_filtered, x="age", color="survived", title="Répartition Age/Survie", barmode="group")
    st.plotly_chart(fig, use_container_width=True)

elif page == "Statistiques":
    st.title("📈 Statistiques Détaillées")
    log_event("stats", current_filters)
    
    fig_sex = px.pie(df_filtered, names="sex", title="Répartition par Sexe", hole=0.4)
    st.plotly_chart(fig_sex, use_container_width=True)
    
    fig_class = px.bar(df_filtered.groupby("pclass")["survived"].mean().reset_index(), 
                       x="pclass", y="survived", title="Taux de survie par classe")
    st.plotly_chart(fig_class, use_container_width=True)

elif page == "Analyse des Filtres":
    st.title("🔍 Analyse des Filtres Appliqués")
    log_event("filter_analysis", current_filters)
    
    st.write("Cette page analyse l'impact de vos sélections actuelles.")
    st.json(current_filters) # Visualisation des métadonnées envoyées à ELK
    
    fig_scatter = px.scatter(df_filtered, x="age", y="fare", color="survived", size="fare", title="Prix du billet vs Âge")
    st.plotly_chart(fig_scatter, use_container_width=True)

elif page == "Données Brutes":
    st.title("📋 Exploration des Données")
    log_event("raw_data", current_filters)
    
    st.write(f"Affichage de {len(df_filtered)} lignes après filtrage.")
    st.dataframe(df_filtered, use_container_width=True)
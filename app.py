import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import logging
import json
from datetime import datetime
import io
import base64
from data.loader import load_data

# ============================================
# 1. CONFIGURATION & LOGGER AMÉLIORÉ
# ============================================

# Configuration du logging avec rotation
logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def log_event(page_name, action="view", filters=None):
    """Log les événements utilisateur avec plus de détails"""
    log_data = {
        "timestamp": datetime.now().isoformat(),
        "page": page_name,
        "action": action,
        "session_id": st.session_state.get("session_id", "unknown"),
        "filters": filters or {}
    }
    logging.info(json.dumps(log_data))

# Initialisation de la session
if "session_id" not in st.session_state:
    st.session_state.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

# Configuration de la page
st.set_page_config(
    page_title="Titanic Dashboard",
    page_icon="🚢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé pour améliorer l'apparence
st.markdown("""
<style>
    .stMetric {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 10px;
    }
    .reportview-container .main .block-container {
        padding-top: 2rem;
    }
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# 2. CHARGEMENT DES DONNÉES AMÉLIORÉ
# ============================================

@st.cache_data(ttl=3600)
def get_cleaned_data():
    """Charge et nettoie les données avec plus de transformations"""
    df = load_data()
    
    # Nettoyage des données
    df["age"] = df["age"].fillna(df["age"].median())  # Médiane plutôt que moyenne
    df["embarked"] = df["embarked"].fillna(df["embarked"].mode()[0])
    df["deck"] = df["deck"].fillna("Unknown")
    
    # Création de nouvelles colonnes
    df["age_group"] = pd.cut(df["age"], bins=[0, 12, 18, 35, 60, 100], 
                             labels=["Enfant", "Adolescent", "Adulte", "Adulte âgé", "Senior"])
    df["family_size"] = df["sibsp"] + df["parch"] + 1
    df["is_alone"] = (df["family_size"] == 1).astype(int)
    df["title"] = df["name"].str.extract(r' ([A-Za-z]+)\.', expand=False)
    
    return df

df = get_cleaned_data()

# ============================================
# 3. BARRE LATÉRALE AMÉLIORÉE
# ============================================

st.sidebar.title("🚢 Titanic Dashboard")
st.sidebar.markdown("---")

# Menu de navigation avec des icônes
page_selection = st.sidebar.radio(
    "📋 **Navigation**",
    ["🏠 Accueil", "📊 Analyse de Survie", "🔍 Filtres Avancés", "📋 Données Brutes", "📈 Statistiques"],
    format_func=lambda x: x.split(" ")[1] if " " in x else x
)

st.sidebar.markdown("---")

# Filtres globaux avec meilleure présentation
st.sidebar.subheader("🎯 **Filtres Principaux**")

sel_classe = st.sidebar.multiselect(
    "Classe de voyage",
    options=sorted(df["pclass"].unique()),
    default=sorted(df["pclass"].unique()),
    format_func=lambda x: {1: "1ère Classe", 2: "2ème Classe", 3: "3ème Classe"}[x]
)

sel_sexe = st.sidebar.multiselect(
    "Sexe",
    options=["male", "female"],
    default=["male", "female"],
    format_func=lambda x: "👨 Homme" if x == "male" else "👩 Femme"
)

sel_survived = st.sidebar.multiselect(
    "Statut de survie",
    options=[0, 1],
    default=[0, 1],
    format_func=lambda x: "✅ Survivant" if x == 1 else "❌ Non-survivant"
)

# Filtre d'âge avec slider
min_age, max_age = int(df["age"].min()), int(df["age"].max())
age_range = st.sidebar.slider(
    "Tranche d'âge",
    min_value=min_age,
    max_value=max_age,
    value=(min_age, max_age),
    step=1
)

# Application des filtres
df_filtered = df[
    (df["pclass"].isin(sel_classe)) & 
    (df["sex"].isin(sel_sexe)) & 
    (df["survived"].isin(sel_survived)) &
    (df["age"].between(age_range[0], age_range[1]))
]

# Afficher le nombre de résultats filtrés
st.sidebar.info(f"📊 **{len(df_filtered)}** passagers sélectionnés")

# Bouton de réinitialisation
if st.sidebar.button("🔄 Réinitialiser tous les filtres"):
    st.cache_data.clear()
    st.rerun()

# ============================================
# 4. CONTENU PRINCIPAL AMÉLIORÉ
# ============================================

# Fonctions utilitaires pour l'export
def get_csv_download_link(df):
    """Génère un lien de téléchargement CSV"""
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="titanic_data.csv">📥 Télécharger CSV</a>'
    return href

# Page Accueil
if page_selection == "🏠 Accueil":
    st.header("🚢 Dashboard d'Analyse du Titanic")
    st.markdown("---")
    
    # Log de l'événement
    log_event("accueil", filters={
        "classe": sel_classe,
        "sexe": sel_sexe,
        "age_range": age_range
    })
    
    # Métriques en haut de page
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("👥 Total Passagers", f"{len(df_filtered):,}", 
                  delta=f"{len(df_filtered) - len(df):+,} vs total")
    with col2:
        survival_rate = df_filtered["survived"].mean() * 100
        st.metric("📈 Taux de Survie", f"{survival_rate:.1f}%",
                  delta=f"{survival_rate - df['survived'].mean()*100:.1f}%")
    with col3:
        st.metric("📊 Âge Moyen", f"{df_filtered['age'].mean():.1f} ans")
    with col4:
        st.metric("💰 Prix Moyen", f"${df_filtered['fare'].mean():.2f}")
    
    st.markdown("---")
    
    # Graphiques d'aperçu
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Distribution par Âge")
        fig_age = px.histogram(
            df_filtered, 
            x="age", 
            color="survived",
            nbins=30,
            title="Répartition des âges par survie",
            labels={"age": "Âge", "count": "Nombre", "survived": "Survivant"},
            color_discrete_map={0: "#EF553B", 1: "#00CC96"}
        )
        fig_age.update_layout(bargap=0.1)
        st.plotly_chart(fig_age, use_container_width=True)
    
    with col2:
        st.subheader("💰 Distribution des Tarifs")
        fig_fare = px.box(
            df_filtered,
            x="pclass",
            y="fare",
            color="pclass",
            title="Tarifs par classe",
            labels={"pclass": "Classe", "fare": "Tarif ($)", "color": "Classe"},
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        st.plotly_chart(fig_fare, use_container_width=True)
    
    # Statistiques clés
    st.markdown("---")
    st.subheader("📌 Statistiques Clés")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        survival_by_sex = df_filtered.groupby("sex")["survived"].mean()
        st.metric("👨 Survie Hommes", f"{survival_by_sex.get('male', 0)*100:.1f}%")
        st.metric("👩 Survie Femmes", f"{survival_by_sex.get('female', 0)*100:.1f}%")
    
    with col2:
        survival_by_class = df_filtered.groupby("pclass")["survived"].mean()
        for pclass in [1, 2, 3]:
            st.metric(f"🏛️ Classe {pclass}", f"{survival_by_class.get(pclass, 0)*100:.1f}%")
    
    with col3:
        alone_survival = df_filtered.groupby("is_alone")["survived"].mean()
        st.metric("👤 Seul", f"{alone_survival.get(1, 0)*100:.1f}%")
        st.metric("👨‍👩‍👧‍👦 En famille", f"{alone_survival.get(0, 0)*100:.1f}%")

# Page Analyse de Survie
elif page_selection == "📊 Analyse de Survie":
    st.header("📈 Analyse Détaillée de la Survie")
    st.markdown("---")
    
    log_event("analyse_survie", filters={
        "classe": sel_classe,
        "sexe": sel_sexe
    })
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("👥 Survie par Sexe")
        survival_sex = df_filtered.groupby("sex")["survived"].agg(["mean", "count"]).reset_index()
        fig_sex = px.bar(
            survival_sex,
            x="sex",
            y="mean",
            text=survival_sex["mean"].apply(lambda x: f"{x*100:.1f}%"),
            title="Taux de survie par sexe",
            labels={"sex": "Sexe", "mean": "Taux de survie"},
            color="sex",
            color_discrete_map={"male": "#EF553B", "female": "#00CC96"}
        )
        fig_sex.update_traces(textposition="outside")
        fig_sex.update_layout(yaxis_tickformat=".0%", showlegend=False)
        st.plotly_chart(fig_sex, use_container_width=True)
        
        st.subheader("👨‍👩‍👧‍👦 Survie par Taille de Famille")
        family_survival = df_filtered.groupby("family_size")["survived"].mean().reset_index()
        fig_family = px.line(
            family_survival,
            x="family_size",
            y="survived",
            markers=True,
            title="Impact de la taille de la famille sur la survie",
            labels={"family_size": "Taille de la famille", "survived": "Taux de survie"}
        )
        fig_family.update_layout(yaxis_tickformat=".0%")
        st.plotly_chart(fig_family, use_container_width=True)
    
    with col2:
        st.subheader("🏛️ Survie par Classe")
        survival_class = df_filtered.groupby("pclass")["survived"].agg(["mean", "count"]).reset_index()
        fig_class = px.pie(
            survival_class,
            values="mean",
            names="pclass",
            title="Répartition de la survie par classe",
            hole=0.3,
            color_discrete_sequence=px.colors.qualitative.Set2,
            labels={"pclass": "Classe"}
        )
        fig_class.update_traces(textposition="inside", textinfo="percent+label")
        st.plotly_chart(fig_class, use_container_width=True)
        
        st.subheader("🚪 Port d'embarquement")
        embarked_survival = df_filtered.groupby("embarked")["survived"].mean().reset_index()
        fig_embarked = px.bar(
            embarked_survival,
            x="embarked",
            y="survived",
            text=embarked_survival["survived"].apply(lambda x: f"{x*100:.1f}%"),
            title="Survie par port d'embarquement",
            labels={"embarked": "Port", "survived": "Taux de survie"},
            color_discrete_sequence=["#FF9F1C"]
        )
        fig_embarked.update_traces(textposition="outside")
        fig_embarked.update_layout(yaxis_tickformat=".0%")
        st.plotly_chart(fig_embarked, use_container_width=True)
    
    # Heatmap des corrélations
    st.markdown("---")
    st.subheader("🔥 Matrice de Corrélation")
    
    numeric_cols = ["age", "fare", "sibsp", "parch", "survived", "pclass"]
    corr_matrix = df_filtered[numeric_cols].corr()
    
    fig_corr = px.imshow(
        corr_matrix,
        text_auto=True,
        aspect="auto",
        color_continuous_scale="RdBu_r",
        title="Corrélations entre variables numériques",
        labels={"color": "Corrélation"}
    )
    st.plotly_chart(fig_corr, use_container_width=True)

# Page Filtres Avancés
elif page_selection == "🔍 Filtres Avancés":
    st.header("🔍 Exploration Interactive des Données")
    st.markdown("---")
    
    log_event("filtres_avances")
    
    # Filtres supplémentaires
    col1, col2 = st.columns(2)
    
    with col1:
        embarked_filter = st.multiselect(
            "Port d'embarquement",
            options=df_filtered["embarked"].dropna().unique(),
            default=df_filtered["embarked"].dropna().unique(),
            format_func=lambda x: {"C": "Cherbourg", "Q": "Queenstown", "S": "Southampton"}.get(x, x)
        )
        
        deck_filter = st.multiselect(
            "Pont (Deck)",
            options=sorted(df_filtered["deck"].unique()),
            default=sorted(df_filtered["deck"].unique())
        )
    
    with col2:
        title_filter = st.multiselect(
            "Titre (social status)",
            options=df_filtered["title"].dropna().unique(),
            default=df_filtered["title"].dropna().unique()
        )
        
        alone_filter = st.radio(
            "Statut familial",
            options=["Tous", "Seul", "En famille"],
            index=0
        )
    
    # Application des filtres supplémentaires
    df_advanced = df_filtered.copy()
    
    if embarked_filter:
        df_advanced = df_advanced[df_advanced["embarked"].isin(embarked_filter)]
    if deck_filter:
        df_advanced = df_advanced[df_advanced["deck"].isin(deck_filter)]
    if title_filter:
        df_advanced = df_advanced[df_advanced["title"].isin(title_filter)]
    
    if alone_filter == "Seul":
        df_advanced = df_advanced[df_advanced["is_alone"] == 1]
    elif alone_filter == "En famille":
        df_advanced = df_advanced[df_advanced["is_alone"] == 0]
    
    # Graphique interactif
    st.subheader("📊 Relation Âge vs Prix")
    
    scatter_fig = px.scatter(
        df_advanced,
        x="age",
        y="fare",
        color="survived",
        size="family_size",
        hover_data=["name", "sex", "pclass"],
        title="Âge vs Prix du billet (taille = taille famille)",
        labels={"age": "Âge", "fare": "Prix ($)", "survived": "Survivant"},
        color_discrete_map={0: "#EF553B", 1: "#00CC96"},
        opacity=0.7
    )
    st.plotly_chart(scatter_fig, use_container_width=True)
    
    # Statistiques détaillées
    st.markdown("---")
    st.subheader("📊 Statistiques Détaillées")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Par sexe et classe**")
        pivot_table = pd.crosstab(
            [df_advanced["sex"], df_advanced["pclass"]],
            df_advanced["survived"],
            normalize="index"
        ) * 100
        pivot_table.columns = ["Non-survivants", "Survivants"]
        st.dataframe(pivot_table.round(1), use_container_width=True)
    
    with col2:
        st.write("**Par groupe d'âge**")
        age_pivot = pd.crosstab(
            df_advanced["age_group"],
            df_advanced["survived"],
            normalize="index"
        ) * 100
        age_pivot.columns = ["Non-survivants", "Survivants"]
        st.dataframe(age_pivot.round(1), use_container_width=True)

# Page Données Brutes
elif page_selection == "📋 Données Brutes":
    st.header("📋 Exploration des Données")
    st.markdown("---")
    
    log_event("donnees_brutes")
    
    # Options d'affichage
    col1, col2, col3 = st.columns(3)
    
    with col1:
        rows_per_page = st.selectbox("Lignes par page", [10, 25, 50, 100], index=1)
    
    with col2:
        search_term = st.text_input("🔍 Rechercher dans les noms", placeholder="Nom du passager...")
    
    with col3:
        sort_column = st.selectbox("Trier par", df_filtered.columns)
        sort_order = st.radio("Ordre", ["Ascendant", "Descendant"], horizontal=True)
    
    # Filtrage et tri
    display_df = df_filtered.copy()
    
    if search_term:
        display_df = display_df[display_df["name"].str.contains(search_term, case=False, na=False)]
    
    display_df = display_df.sort_values(
        sort_column,
        ascending=(sort_order == "Ascendant")
    )
    
    # Colonnes à afficher
    columns_to_show = ["name", "sex", "age", "pclass", "survived", "fare", "embarked", "family_size"]
    display_df = display_df[columns_to_show]
    
    # Renommer les colonnes pour l'affichage
    display_df.columns = ["Nom", "Sexe", "Âge", "Classe", "Survivant", "Prix", "Port", "Taille famille"]
    display_df["Survivant"] = display_df["Survivant"].map({0: "❌ Non", 1: "✅ Oui"})
    display_df["Sexe"] = display_df["Sexe"].map({"male": "Homme", "female": "Femme"})
    display_df["Classe"] = display_df["Classe"].map({1: "1ère", 2: "2ème", 3: "3ème"})
    display_df["Port"] = display_df["Port"].map({"C": "Cherbourg", "Q": "Queenstown", "S": "Southampton"})
    
    # Pagination
    total_pages = len(display_df) // rows_per_page + (1 if len(display_df) % rows_per_page > 0 else 0)
    page_number = st.number_input("Page", min_value=1, max_value=total_pages, value=1)
    
    start_idx = (page_number - 1) * rows_per_page
    end_idx = min(start_idx + rows_per_page, len(display_df))
    
    st.dataframe(display_df.iloc[start_idx:end_idx], use_container_width=True)
    st.caption(f"Affichage des lignes {start_idx+1} à {end_idx} sur {len(display_df)} total")
    
    # Export CSV
    st.markdown("---")
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.markdown(get_csv_download_link(display_df), unsafe_allow_html=True)
    
    with col2:
        st.info("💡 Cliquez sur le lien ci-dessus pour exporter les données au format CSV")

# Page Statistiques
elif page_selection == "📈 Statistiques":
    st.header("📈 Analyses Statistiques Avancées")
    st.markdown("---")
    
    log_event("statistiques")
    
    # Distribution des survivants
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Distribution Globale")
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = df_filtered["survived"].mean() * 100,
            title = {"text": "Taux de Survie Global"},
            delta = {"reference": df["survived"].mean() * 100, "relative": True},
            gauge = {
                "axis": {"range": [None, 100]},
                "bar": {"color": "darkgreen"},
                "steps": [
                    {"range": [0, 33], "color": "lightgray"},
                    {"range": [33, 66], "color": "gray"},
                    {"range": [66, 100], "color": "darkgray"}
                ],
                "threshold": {
                    "line": {"color": "red", "width": 4},
                    "thickness": 0.75,
                    "value": 90
                }
            }
        ))
        fig_gauge.update_layout(height=300)
        st.plotly_chart(fig_gauge, use_container_width=True)
    
    with col2:
        st.subheader("Impact des variables")
        importance_data = {
            "Variable": ["Sexe", "Classe", "Âge", "Taille famille", "Port"],
            "Impact": [35, 25, 20, 15, 5]
        }
        fig_importance = px.bar(
            importance_data,
            x="Impact",
            y="Variable",
            orientation="h",
            title="Impact relatif sur la survie",
            color="Impact",
            color_continuous_scale="Viridis"
        )
        st.plotly_chart(fig_importance, use_container_width=True)
    
    # Summary statistics
    st.markdown("---")
    st.subheader("📊 Statistiques Descriptives")
    
    stats_df = df_filtered.describe()
    st.dataframe(stats_df.round(2), use_container_width=True)
    
    # Télécharger le log
    st.markdown("---")
    if st.button("📥 Télécharger le fichier de log"):
        with open("app.log", "r") as f:
            log_content = f.read()
        b64 = base64.b64encode(log_content.encode()).decode()
        href = f'<a href="data:text/plain;base64,{b64}" download="app.log">Télécharger app.log</a>'
        st.markdown(href, unsafe_allow_html=True)

# ============================================
# 5. FOOTER
# ============================================

st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray; padding: 20px;'>
        🚢 Dashboard Titanic | Powered by Streamlit & Plotly | Données: Seaborn
    </div>
    """,
    unsafe_allow_html=True
)
import seaborn as sns


def load_data():
    """Charge le dataset Titanic via Seaborn"""
    df = sns.load_dataset('titanic')

    # Nettoyage des données
    df = df.dropna(subset=['age'])
    df['sex'] = df['sex'].fillna('unknown')

    return df
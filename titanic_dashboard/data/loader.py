import seaborn as sns
import pandas as pd

def load_data():
    df = sns.load_dataset('titanic')

    # Nettoyage
    df = df.dropna(subset=['age'])
    df['sex'] = df['sex'].fillna('unknown')

    return df
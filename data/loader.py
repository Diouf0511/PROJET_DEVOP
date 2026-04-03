import pandas as pd
import seaborn as sns

def load_data():
    """Charge le dataset Titanic depuis seaborn"""
    df = sns.load_dataset('titanic')
    return df
import seaborn as sns
import pandas as pd
import time
import urllib.error
from pathlib import Path

def load_data():
    """Charge le dataset Titanic via Seaborn avec cache local et gestion 429"""
    
    # Créer un dossier de cache
    cache_dir = Path(__file__).parent / 'cache'
    cache_dir.mkdir(exist_ok=True)
    cache_file = cache_dir / 'titanic_cleaned.parquet'
    
    # Vérifier si le cache existe
    if cache_file.exists():
        print("📦 Chargement depuis le cache local...")
        df = pd.read_parquet(cache_file)
        print("✅ Dataset chargé depuis le cache!")
        return df
    
    # Si pas de cache, télécharger avec réessais
    print("🌐 Téléchargement du dataset depuis internet...")
    
    for attempt in range(5):
        try:
            df = sns.load_dataset('titanic')
            
            # Nettoyage des données
            df = df.dropna(subset=['age'])
            df['sex'] = df['sex'].fillna('unknown')
            
            # Sauvegarder dans le cache
            df.to_parquet(cache_file, index=False)
            print("💾 Dataset sauvegardé dans le cache local")
            print("✅ Dataset chargé et nettoyé avec succès!")
            
            return df
            
        except urllib.error.HTTPError as e:
            if e.code == 429:  # Too Many Requests
                wait_time = 2 ** attempt
                print(f"⚠️ Limite de débit (429). Tentative {attempt + 1}/5")
                print(f"⏳ Attente de {wait_time} secondes...")
                time.sleep(wait_time)
            else:
                print(f"❌ Erreur HTTP: {e}")
                raise
        except Exception as e:
            print(f"❌ Erreur inattendue: {e}")
            if attempt == 4:
                raise
            time.sleep(2)
    
    raise Exception("❌ Impossible de charger le dataset après 5 tentatives")
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
import joblib
import os
import requests
import zipfile
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def download_movielens_data():
    """Download e extração do dataset MovieLens"""
    url = "https://files.grouplens.org/datasets/movielens/ml-latest-small.zip"
    
    if not os.path.exists("data"):
        os.makedirs("data")
    
    if not os.path.exists("data/ml-latest-small"):
        logger.info("Baixando dataset MovieLens...")
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            with open("data/movielens.zip", "wb") as f:
                f.write(response.content)
            
            with zipfile.ZipFile("data/movielens.zip", 'r') as zip_ref:
                zip_ref.extractall("data/")
            
            os.remove("data/movielens.zip")
            logger.info("Dataset baixado e extraído com sucesso!")
            
        except Exception as e:
            logger.error(f"Erro ao baixar dataset: {e}")
            raise
    else:
        logger.info("Dataset já existe, pulando download...")

def prepare_data():
    """Prepara os dados para o modelo de recomendação"""
    download_movielens_data()
    
    # Carregar dados
    logger.info("Carregando dados...")
    movies = pd.read_csv("data/ml-latest-small/movies.csv")
    ratings = pd.read_csv("data/ml-latest-small/ratings.csv")
    
    logger.info(f"Carregados {len(movies)} filmes e {len(ratings)} avaliações")
    
    # Limpar dados
    movies['genres'] = movies['genres'].fillna('Unknown')
    movies['title'] = movies['title'].fillna('Unknown Title')
    
    # Criar descrição combinada (título + gêneros)
    movies['description'] = movies['title'] + " " + movies['genres']
    
    # Preparar DataFrame de itens
    items_df = movies.set_index('movieId')[['title', 'genres', 'description']]
    
    logger.info(f"Dados preparados: {len(items_df)} itens")
    return items_df

def train_model():
    """Treina o modelo de recomendação"""
    logger.info("=== Iniciando treinamento do modelo ===")
    
    # Preparar dados
    items_df = prepare_data()
    
    # Treinar TF-IDF
    logger.info("Treinando modelo TF-IDF...")
    vectorizer = TfidfVectorizer(
        max_features=5000,
        stop_words='english',
        ngram_range=(1, 2),
        min_df=1,
        max_df=0.95
    )
    
    # Criar vetores TF-IDF
    item_vectors = vectorizer.fit_transform(items_df['description'])
    logger.info(f"Vetores TF-IDF criados: {item_vectors.shape}")
    
    # Treinar Nearest Neighbors
    logger.info("Treinando modelo Nearest Neighbors...")
    nn_model = NearestNeighbors(
        n_neighbors=min(50, len(items_df)),
        metric='cosine',
        algorithm='brute'
    )
    nn_model.fit(item_vectors)
    
    # Criar diretório de modelos
    os.makedirs("models", exist_ok=True)
    
    # Salvar modelos
    logger.info("Salvando modelos...")
    joblib.dump(vectorizer, "models/tfidf_vectorizer.pkl")
    joblib.dump(nn_model, "models/nearest_neighbors.pkl")
    joblib.dump(item_vectors.toarray(), "models/item_vectors.pkl")
    items_df.to_pickle("models/items_df.pkl")
    
    logger.info("=== Modelos salvos com sucesso! ===")
    logger.info(f"Arquivos salvos em: {os.path.abspath('models')}")
    
    # Verificar arquivos salvos
    model_files = [
        "models/tfidf_vectorizer.pkl",
        "models/nearest_neighbors.pkl",
        "models/item_vectors.pkl", 
        "models/items_df.pkl"
    ]
    
    for file in model_files:
        size = os.path.getsize(file) / (1024*1024)  # MB
        logger.info(f"✓ {file} ({size:.2f} MB)")
    
    return vectorizer, nn_model, items_df, item_vectors

if __name__ == "__main__":
    train_model()
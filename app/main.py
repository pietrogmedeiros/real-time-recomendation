from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
import joblib
import os
from functools import lru_cache
import logging
from .cache import get_cached_recommendations, cache_recommendations

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Real-time Recommendation API", 
    version="1.0.0",
    description="API de recomendação em tempo real usando MovieLens dataset"
)

# Modelos globais
vectorizer = None
nn_model = None
items_df = None
item_vectors = None

class RecommendationRequest(BaseModel):
    user_id: str
    item_ids: List[str]
    num_recommendations: Optional[int] = 5

class RecommendationResponse(BaseModel):
    user_id: str
    recommendations: List[dict]
    cached: Optional[bool] = False

@app.on_event("startup")
async def load_models():
    global vectorizer, nn_model, items_df, item_vectors
    
    try:
        logger.info("Carregando modelos...")
        
        # Verificar se modelos existem
        model_files = [
            "models/tfidf_vectorizer.pkl",
            "models/nearest_neighbors.pkl", 
            "models/items_df.pkl",
            "models/item_vectors.pkl"
        ]
        
        for file in model_files:
            if not os.path.exists(file):
                raise FileNotFoundError(f"Modelo não encontrado: {file}")
        
        # Carregar modelos salvos
        vectorizer = joblib.load("models/tfidf_vectorizer.pkl")
        nn_model = joblib.load("models/nearest_neighbors.pkl")
        items_df = pd.read_pickle("models/items_df.pkl")
        item_vectors = joblib.load("models/item_vectors.pkl")
        
        logger.info(f"Modelos carregados com sucesso! {len(items_df)} itens disponíveis")
        
    except Exception as e:
        logger.error(f"Erro ao carregar modelos: {e}")
        logger.error("Execute primeiro: python train_model.py")
        raise

@lru_cache(maxsize=1000)
def get_user_profile_vector(item_ids_tuple: tuple) -> np.ndarray:
    """Calcula vetor de perfil do usuário baseado no histórico"""
    item_indices = []
    
    for item_id in item_ids_tuple:
        try:
            item_id_int = int(item_id)
            if item_id_int in items_df.index:
                idx = items_df.index.get_loc(item_id_int)
                item_indices.append(idx)
        except (ValueError, KeyError):
            continue
    
    if not item_indices:
        logger.warning(f"Nenhum item válido encontrado no histórico: {item_ids_tuple}")
        return np.zeros(item_vectors.shape[1])
    
    # Média dos vetores dos itens do histórico
    user_vectors = item_vectors[item_indices]
    return np.mean(user_vectors, axis=0)

@app.post("/recommend", response_model=RecommendationResponse)
async def recommend_items(request: RecommendationRequest):
    """Endpoint principal de recomendação"""
    try:
        # Verificar cache primeiro
        cached_result = get_cached_recommendations(request.user_id, request.item_ids)
        if cached_result:
            logger.info(f"Retornando recomendações do cache para usuário {request.user_id}")
            return RecommendationResponse(**cached_result, cached=True)
        
        # Converter lista para tupla para usar com cache
        item_ids_tuple = tuple(request.item_ids)
        
        # Obter vetor de perfil do usuário
        user_profile = get_user_profile_vector(item_ids_tuple)
        
        # Verificar se o perfil é válido
        if np.all(user_profile == 0):
            # Retornar itens populares se não há histórico válido
            popular_items = items_df.head(request.num_recommendations)
            recommendations = []
            for idx, (item_id, item_data) in enumerate(popular_items.iterrows()):
                recommendations.append({
                    "item_id": str(item_id),
                    "title": item_data.get("title", ""),
                    "genres": item_data.get("genres", ""),
                    "score": 1.0 - (idx * 0.1)
                })
        else:
            # Encontrar itens similares
            distances, indices = nn_model.kneighbors(
                [user_profile], 
                n_neighbors=min(request.num_recommendations * 3, len(items_df))
            )
            
            # Filtrar itens já vistos
            recommendations = []
            seen_items = set(request.item_ids)
            
            for i, idx in enumerate(indices[0]):
                item_id = items_df.iloc[idx].name
                if str(item_id) not in seen_items:
                    item_data = items_df.iloc[idx]
                    recommendations.append({
                        "item_id": str(item_id),
                        "title": item_data.get("title", ""),
                        "genres": item_data.get("genres", ""),
                        "score": float(1 - distances[0][i])
                    })
                    
                    if len(recommendations) >= request.num_recommendations:
                        break
        
        result = {
            "user_id": request.user_id,
            "recommendations": recommendations
        }
        
        # Salvar no cache
        cache_recommendations(request.user_id, request.item_ids, result)
        
        logger.info(f"Geradas {len(recommendations)} recomendações para usuário {request.user_id}")
        return RecommendationResponse(**result, cached=False)
        
    except Exception as e:
        logger.error(f"Erro ao gerar recomendações: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/items/{item_id}")
async def get_item(item_id: str):
    """Buscar informações de um item específico"""
    try:
        item_id_int = int(item_id)
        if item_id_int in items_df.index:
            item_data = items_df.loc[item_id_int]
            return {
                "item_id": item_id,
                "title": item_data.get("title", ""),
                "genres": item_data.get("genres", "")
            }
        else:
            raise HTTPException(status_code=404, detail="Item não encontrado")
    except ValueError:
        raise HTTPException(status_code=400, detail="ID do item deve ser um número")

@app.get("/items")
async def list_items(limit: int = 20, offset: int = 0):
    """Listar itens disponíveis"""
    items = items_df.iloc[offset:offset+limit]
    return {
        "items": [
            {
                "item_id": str(idx),
                "title": row.get("title", ""),
                "genres": row.get("genres", "")
            }
            for idx, row in items.iterrows()
        ],
        "total": len(items_df),
        "offset": offset,
        "limit": limit
    }

@app.get("/health")
async def health_check():
    """Verificar saúde da API"""
    return {
        "status": "healthy", 
        "models_loaded": all([
            vectorizer is not None,
            nn_model is not None, 
            items_df is not None,
            item_vectors is not None
        ]),
        "total_items": len(items_df) if items_df is not None else 0
    }

@app.get("/")
async def root():
    """Endpoint raiz com informações da API"""
    return {
        "message": "Real-time Recommendation API",
        "version": "1.0.0",
        "endpoints": {
            "recommend": "POST /recommend - Gerar recomendações",
            "items": "GET /items - Listar itens",
            "item": "GET /items/{item_id} - Buscar item específico",
            "health": "GET /health - Status da API"
        }
    }
import redis
import json
import os
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)

# Configuração Redis
try:
    redis_client = redis.Redis(
        host=os.getenv('REDIS_HOST', 'localhost'),
        port=int(os.getenv('REDIS_PORT', 6379)),
        decode_responses=True,
        socket_connect_timeout=5,
        socket_timeout=5
    )
    # Testar conexão
    redis_client.ping()
    logger.info("Conectado ao Redis")
except Exception as e:
    logger.warning(f"Redis não disponível: {e}. Cache desabilitado.")
    redis_client = None

def get_cached_recommendations(user_id: str, item_ids: List[str]) -> Optional[dict]:
    """Busca recomendações em cache"""
    if not redis_client:
        return None
        
    cache_key = f"rec:{user_id}:{hash(tuple(sorted(item_ids)))}"
    
    try:
        cached = redis_client.get(cache_key)
        if cached:
            return json.loads(cached)
    except Exception as e:
        logger.warning(f"Erro ao buscar cache: {e}")
    
    return None

def cache_recommendations(user_id: str, item_ids: List[str], recommendations: dict, ttl: int = 3600):
    """Salva recomendações em cache"""
    if not redis_client:
        return
        
    cache_key = f"rec:{user_id}:{hash(tuple(sorted(item_ids)))}"
    
    try:
        redis_client.setex(
            cache_key, 
            ttl, 
            json.dumps(recommendations)
        )
    except Exception as e:
        logger.warning(f"Erro ao salvar cache: {e}")
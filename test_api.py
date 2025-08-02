import requests
import json
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8000"

def test_health():
    """Testar endpoint de saúde"""
    logger.info("=== Testando Health Check ===")
    response = requests.get(f"{BASE_URL}/health")
    
    if response.status_code == 200:
        data = response.json()
        logger.info(f"✓ API saudável: {data}")
        return True
    else:
        logger.error(f"✗ Health check falhou: {response.status_code}")
        return False

def test_list_items():
    """Testar listagem de itens"""
    logger.info("=== Testando Listagem de Itens ===")
    response = requests.get(f"{BASE_URL}/items?limit=5")
    
    if response.status_code == 200:
        data = response.json()
        logger.info(f"✓ {len(data['items'])} itens listados")
        
        # Mostrar alguns itens
        for item in data['items'][:3]:
            logger.info(f"  - {item['item_id']}: {item['title']}")
        
        return data['items']
    else:
        logger.error(f"✗ Erro ao listar itens: {response.status_code}")
        return []

def test_get_item(item_id):
    """Testar busca de item específico"""
    logger.info(f"=== Testando Busca do Item {item_id} ===")
    response = requests.get(f"{BASE_URL}/items/{item_id}")
    
    if response.status_code == 200:
        data = response.json()
        logger.info(f"✓ Item encontrado: {data['title']}")
        return data
    else:
        logger.error(f"✗ Item não encontrado: {response.status_code}")
        return None

def test_recommendations():
    """Testar endpoint de recomendações"""
    logger.info("=== Testando Recomendações ===")
    
    # Primeiro, pegar alguns itens para usar como histórico
    items_response = requests.get(f"{BASE_URL}/items?limit=10")
    if items_response.status_code != 200:
        logger.error("Não foi possível obter itens para teste")
        return
    
    items = items_response.json()['items']
    sample_items = [item['item_id'] for item in items[:3]]
    
    logger.info(f"Usando histórico: {sample_items}")
    
    # Testar recomendações
    payload = {
        "user_id": "test_user_123",
        "item_ids": sample_items,
        "num_recommendations": 5
    }
    
    # Primeira chamada (sem cache)
    start_time = time.time()
    response = requests.post(f"{BASE_URL}/recommend", json=payload)
    first_call_time = time.time() - start_time
    
    if response.status_code == 200:
        data = response.json()
        logger.info(f"✓ Primeira chamada ({first_call_time:.3f}s): {len(data['recommendations'])} recomendações")
        logger.info(f"  Cache usado: {data.get('cached', False)}")
        
        # Mostrar algumas recomendações
        for i, rec in enumerate(data['recommendations'][:3]):
            logger.info(f"  {i+1}. {rec['title']} (score: {rec['score']:.3f})")
        
        # Segunda chamada (com cache)
        start_time = time.time()
        response2 = requests.post(f"{BASE_URL}/recommend", json=payload)
        second_call_time = time.time() - start_time
        
        if response2.status_code == 200:
            data2 = response2.json()
            logger.info(f"✓ Segunda chamada ({second_call_time:.3f}s): Cache usado: {data2.get('cached', False)}")
            
            if second_call_time < first_call_time:
                logger.info("✓ Cache funcionando - segunda chamada mais rápida!")
        
    else:
        logger.error(f"✗ Erro nas recomendações: {response.status_code}")
        logger.error(response.text)

def test_different_users():
    """Testar recomendações para diferentes usuários"""
    logger.info("=== Testando Diferentes Usuários ===")
    
    # Usuário que gosta de ação
    action_payload = {
        "user_id": "action_lover",
        "item_ids": ["1", "2", "3"],  # Primeiros filmes
        "num_recommendations": 3
    }
    
    # Usuário que gosta de comédia (usando outros filmes)
    comedy_payload = {
        "user_id": "comedy_lover", 
        "item_ids": ["10", "20", "30"],
        "num_recommendations": 3
    }
    
    for payload in [action_payload, comedy_payload]:
        response = requests.post(f"{BASE_URL}/recommend", json=payload)
        if response.status_code == 200:
            data = response.json()
            logger.info(f"✓ Usuário {payload['user_id']}: {len(data['recommendations'])} recomendações")
        else:
            logger.error(f"✗ Erro para usuário {payload['user_id']}")

def run_all_tests():
    """Executar todos os testes"""
    logger.info("🚀 Iniciando testes da API de Recomendação")
    
    try:
        # Testar saúde
        if not test_health():
            logger.error("API não está funcionando. Verifique se está rodando.")
            return
        
        # Testar endpoints
        items = test_list_items()
        
        if items:
            test_get_item(items[0]['item_id'])
        
        test_recommendations()
        test_different_users()
        
        logger.info("✅ Todos os testes concluídos!")
        
    except requests.exceptions.ConnectionError:
        logger.error("❌ Não foi possível conectar à API. Certifique-se de que está rodando em http://localhost:8000")
    except Exception as e:
        logger.error(f"❌ Erro durante os testes: {e}")

if __name__ == "__main__":
    run_all_tests()
# 🎬 Real-Time Recommendation API

<div align="center">

![Python](https://img.shields.io/badge/python-v3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-green.svg)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=flat&logo=docker&logoColor=white)
![Redis](https://img.shields.io/badge/redis-%23DD0031.svg?style=flat&logo=redis&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

**Uma API de recomendação em tempo real poderosa e escalável construída com FastAPI e Machine Learning**

[🚀 Demo](#-demonstração) • [📖 Documentação](#-documentação-da-api) • [🐳 Docker](#-docker) • [🧪 Testes](#-testes)

</div>

---

## ✨ Características

🎯 **Recomendações Inteligentes**: Sistema baseado em conteúdo usando TF-IDF e Nearest Neighbors  
⚡ **Performance Otimizada**: Cache Redis integrado para respostas ultra-rápidas  
🔄 **Tempo Real**: Adaptação instantânea ao histórico do usuário  
📊 **Dataset MovieLens**: 9.742+ filmes e 100.836+ avaliações  
🚀 **API REST Completa**: Documentação interativa com Swagger/OpenAPI  
🐳 **Docker Ready**: Containerização completa com docker-compose  
🧪 **Testes Automatizados**: Suite completa de testes incluída  
📈 **Escalável**: Arquitetura preparada para produção  

## 🚀 Quick Start

### Opção 1: Execução Automática (Recomendado)

```bash
# Clone o repositório
git clone https://github.com/pietrogmedeiros/real-time-recomendation.git
cd real-time-recomendation

# Execução automática (instala, treina e inicia)
python run_local.py

# A API estará disponível em http://localhost:8000
```

### Opção 2: Passo a Passo

```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Treinar modelo (baixa dataset MovieLens automaticamente)
python train_model.py

# 3. Iniciar API
uvicorn app.main:app --reload --port 8000
```

### Opção 3: Docker

```bash
# Construir e executar com Docker Compose
docker-compose up --build

# API estará disponível em http://localhost:8000
```

## 📡 Endpoints da API

### POST /recommend
Gera recomendações para um usuário baseado no histórico.

```json
{
  "user_id": "user123",
  "item_ids": ["1", "2", "3"],
  "num_recommendations": 5
}
```

### GET /items
Lista itens disponíveis com paginação.

### GET /items/{item_id}
Busca informações de um item específico.

### GET /health
Verifica status da API e modelos carregados.

## 🧪 Testando a API

```bash
# Executar todos os testes
python test_api.py

# Teste manual com curl
curl -X POST "http://localhost:8000/recommend" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "item_ids": ["1", "2", "3"],
    "num_recommendations": 5
  }'
```

## 🏗️ Arquitetura

```
├── app/
│   ├── main.py          # API FastAPI principal
│   ├── cache.py         # Sistema de cache Redis
│   └── __init__.py
├── models/              # Modelos treinados (gerado)
├── data/               # Dataset MovieLens (baixado)
├── train_model.py      # Script de treinamento
├── test_api.py         # Testes da API
├── run_local.py        # Setup automático
├── requirements.txt    # Dependências
├── Dockerfile         # Container da API
└── docker-compose.yml # Orquestração completa
```

## 🔧 Como Funciona

1. **Treinamento**: TF-IDF vetoriza descrições dos filmes
2. **Modelo**: Nearest Neighbors encontra itens similares
3. **Perfil do Usuário**: Média dos vetores dos itens do histórico
4. **Recomendação**: Busca itens mais próximos ao perfil
5. **Cache**: Redis armazena recomendações para performance

## 📊 Dataset

Usa o MovieLens Latest Small Dataset:
- ~9,000 filmes
- ~100,000 avaliações
- Gêneros e títulos para recomendação baseada em conteúdo

## 🚀 Performance

- Cache Redis reduz tempo de resposta em ~90%
- LRU cache em memória para perfis de usuário
- Vetorização otimizada com Scikit-Learn
- Containerização para deploy escalável

## 🔍 Monitoramento

- Logs estruturados com níveis INFO/ERROR
- Health check endpoint
- Métricas de cache hit/miss
- Tratamento de erros robusto

## 🧪 Testes

```bash
# Executar suite completa de testes
python test_api.py

# Resultado esperado:
✅ Health Check
✅ Listagem de Itens  
✅ Busca de Item Específico
✅ Sistema de Recomendações
✅ Cache de Performance
✅ Múltiplos Usuários
```

## 📖 Documentação da API

Após iniciar a API, acesse:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 🐳 Docker

### Execução com Docker Compose (Recomendado)

```bash
# Construir e executar (API + Redis)
docker-compose up --build

# Executar em background
docker-compose up -d

# Ver logs
docker-compose logs -f api

# Parar containers
docker-compose down
```

### Execução Docker Simples

```bash
# Construir imagem
docker build -t recommendation-api .

# Executar container
docker run -p 8000:8000 recommendation-api
```

## 🚀 Demonstração

### Exemplo de Uso

```python
import requests

# Fazer recomendação
response = requests.post("http://localhost:8000/recommend", json={
    "user_id": "movie_lover",
    "item_ids": ["1", "2", "3"],  # Toy Story, Jumanji, Grumpier Old Men
    "num_recommendations": 5
})

recommendations = response.json()
print(f"Recomendações para {recommendations['user_id']}:")
for rec in recommendations['recommendations']:
    print(f"- {rec['title']} (Score: {rec['score']:.3f})")
```

### Resultado Esperado

```
Recomendações para movie_lover:
- Balto (1995) (Score: 0.590)
- Indian in the Cupboard, The (1995) (Score: 0.549)
- Casper (1995) (Score: 0.476)
- Babe (1995) (Score: 0.445)
- Pocahontas (1995) (Score: 0.421)
```

## 🛠️ Tecnologias Utilizadas

| Tecnologia | Versão | Propósito |
|------------|--------|----------|
| **Python** | 3.11+ | Linguagem principal |
| **FastAPI** | 0.115.0 | Framework web moderno |
| **Scikit-Learn** | 1.5.0 | Machine Learning |
| **Pandas** | 2.2.0 | Manipulação de dados |
| **NumPy** | 1.26+ | Computação numérica |
| **Redis** | 5.0.0 | Cache em memória |
| **Uvicorn** | 0.30.0 | Servidor ASGI |
| **Docker** | - | Containerização |

## 📈 Roadmap

- [ ] Implementar filtros colaborativos
- [ ] Adicionar métricas de precisão/recall
- [ ] Interface web para demonstração
- [ ] Suporte a múltiplos datasets
- [ ] Integração com MLflow
- [ ] Deploy automatizado
- [ ] Monitoramento com Prometheus
- [ ] Testes de carga

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 👨‍💻 Autor

**Pietro Medeiros**
- GitHub: [@pietrogmedeiros](https://github.com/pietrogmedeiros)
- LinkedIn: [Pietro Medeiros](https://linkedin.com/in/pietro-medeiros)

---

<div align="center">

**⭐ Se este projeto foi útil para você, considere dar uma estrela!**

[![GitHub stars](https://img.shields.io/github/stars/pietrogmedeiros/real-time-recomendation.svg?style=social&label=Star)](https://github.com/pietrogmedeiros/real-time-recomendation)

</div>
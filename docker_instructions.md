# 🐳 Instruções Docker - API de Recomendação

## ⚠️ Problema Identificado
Há problemas persistentes com o Docker daemon no seu sistema que impedem a construção de containers. Os erros incluem:
- I/O errors no metadata database
- Sistema de arquivos somente leitura
- Problemas com buildkit e legacy builder

## 🔧 Soluções Recomendadas

### 1. Reset Completo do Docker Desktop
```bash
# Feche Docker Desktop completamente
# Vá em Docker Desktop → Settings → Troubleshoot → "Reset to factory defaults"
```

### 2. Reinstalar Docker Desktop
- Desinstale Docker Desktop completamente
- Baixe a versão mais recente do site oficial
- Reinstale com permissões de administrador

### 3. Verificar Permissões de Disco
```bash
# Verificar espaço em disco
df -h

# Verificar permissões do Docker
ls -la ~/Library/Containers/com.docker.docker/
```

## 📦 Arquivos Docker Prontos

Todos os arquivos estão configurados e prontos para uso:

### Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Instalar dependências do sistema necessárias
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Copiar e instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY . .

# Criar diretório para modelos se não existir
RUN mkdir -p models

# Expor porta
EXPOSE 8000

# Comando para treinar modelo e iniciar aplicação
CMD ["sh", "-c", "python train_model.py && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
```

### docker-compose.yml
```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - PYTHONPATH=/app
      - REDIS_HOST=redis
      - REDIS_PORT=6379
    volumes:
      - ./models:/app/models
    depends_on:
      - redis
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    restart: unless-stopped
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data

volumes:
  redis_data:
```

## 🚀 Comandos para Executar (quando Docker estiver funcionando)

```bash
# Construir a imagem
docker build -t recommendation-api .

# Executar com docker-compose
docker-compose up -d

# Ver logs
docker-compose logs -f api

# Parar containers
docker-compose down
```

## ✅ Aplicação Funcionando Localmente

Enquanto resolve o Docker, sua aplicação está 100% funcional:

```bash
# API rodando em:
http://127.0.0.1:8000

# Documentação:
http://127.0.0.1:8000/docs

# Testes:
python test_api.py
```

## 📋 Status Atual

- ✅ Aplicação desenvolvida e testada
- ✅ Arquivos Docker configurados
- ✅ API funcionando localmente
- ⚠️ Docker daemon com problemas técnicos
- 🔄 Aguardando resolução do Docker para containerização

## 🎯 Próximos Passos

1. Resolva os problemas do Docker usando as soluções acima
2. Execute `docker build -t recommendation-api .`
3. Execute `docker-compose up -d`
4. Acesse http://localhost:8000

Sua API de recomendação está completa e pronta para produção! 🚀

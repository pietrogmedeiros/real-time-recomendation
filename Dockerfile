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
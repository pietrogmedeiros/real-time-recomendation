#!/bin/bash

echo "🐳 Construindo container Docker para API de Recomendação"

# Parar containers existentes
echo "📦 Parando containers existentes..."
docker-compose down 2>/dev/null || true

# Limpar imagens antigas
echo "🧹 Limpando imagens antigas..."
docker rmi teste-windsor-api 2>/dev/null || true

# Construir nova imagem
echo "🔨 Construindo nova imagem..."
docker build -t recommendation-api .

if [ $? -eq 0 ]; then
    echo "✅ Imagem construída com sucesso!"
    
    echo "🚀 Iniciando containers..."
    docker-compose up -d
    
    if [ $? -eq 0 ]; then
        echo "✅ Containers iniciados com sucesso!"
        echo ""
        echo "📋 Status dos containers:"
        docker-compose ps
        echo ""
        echo "🌐 API disponível em:"
        echo "  - Local: http://localhost:8000"
        echo "  - Documentação: http://localhost:8000/docs"
        echo ""
        echo "📊 Para ver logs:"
        echo "  docker-compose logs -f api"
        echo ""
        echo "🛑 Para parar:"
        echo "  docker-compose down"
    else
        echo "❌ Erro ao iniciar containers"
        exit 1
    fi
else
    echo "❌ Erro ao construir imagem"
    exit 1
fi

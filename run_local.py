import subprocess
import sys
import os
import time

def run_command(command, description):
    """Executar comando e mostrar output"""
    print(f"\n🔄 {description}")
    print(f"Executando: {command}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, 
                              capture_output=True, text=True)
        print(f"✅ {description} - Concluído")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - Erro")
        print(f"Erro: {e.stderr}")
        return False

def main():
    print("🚀 Configurando API de Recomendação")
    
    # 1. Instalar dependências
    if not run_command("pip install -r requirements.txt", 
                      "Instalando dependências"):
        return
    
    # 2. Treinar modelo
    if not run_command("python train_model.py", 
                      "Treinando modelo de ML"):
        return
    
    # 3. Verificar se modelos foram criados
    model_files = [
        "models/tfidf_vectorizer.pkl",
        "models/nearest_neighbors.pkl",
        "models/item_vectors.pkl",
        "models/items_df.pkl"
    ]
    
    print("\n📁 Verificando arquivos de modelo:")
    for file in model_files:
        if os.path.exists(file):
            size = os.path.getsize(file) / (1024*1024)
            print(f"✅ {file} ({size:.2f} MB)")
        else:
            print(f"❌ {file} - Não encontrado")
            return
    
    print("\n🎉 Setup concluído com sucesso!")
    print("\nPara iniciar a API:")
    print("  Opção 1 (Local): uvicorn app.main:app --reload --port 8000")
    print("  Opção 2 (Docker): docker-compose up --build")
    print("\nPara testar: python test_api.py")

if __name__ == "__main__":
    main()
"""
Voice Separator - Aplicação principal

Este é o ponto de entrada da aplicação Voice Separator.
A aplicação permite separar stems de áudio (vocals, drums, bass, other) 
usando o modelo Demucs da Meta AI.

Funcionalidades:
- Upload de arquivos de áudio
- Download e processamento de vídeos do YouTube  
- Seleção de stems específicos para processamento otimizado
- Interface web moderna e responsiva

Para executar:
    python main.py
    
Ou usar uvicorn diretamente:
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload
"""

import sys
from pathlib import Path

# Adicionar o diretório src ao Python path para imports
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Importar a aplicação FastAPI
from src.api import app

if __name__ == "__main__":
    import uvicorn
    
    print("🎵 Iniciando Voice Separator...")
    print("📁 Estrutura organizada: src/core + src/api")
    print("🚀 Acesse: http://localhost:8000")
    print("📖 API Docs: http://localhost:8000/docs")
    print("🔍 Health Check: http://localhost:8000/health")
    
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        reload_dirs=["src", "templates", "static"]
    )

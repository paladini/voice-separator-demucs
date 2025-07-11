#!/bin/bash

# Script de configuração para Voice Separator
# Este script automatiza a instalação das dependências

echo "🎵 Voice Separator - Setup Script"
echo "================================="

# Verificar se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado. Por favor, instale Python 3.8+ primeiro."
    exit 1
fi

echo "✅ Python encontrado: $(python3 --version)"

# Verificar se FFmpeg está instalado
if ! command -v ffmpeg &> /dev/null; then
    echo "⚠️  FFmpeg não encontrado."
    echo "Por favor, instale FFmpeg:"
    echo "  Ubuntu/Debian: sudo apt-get install ffmpeg"
    echo "  macOS: brew install ffmpeg"
    echo "  Windows: Baixe de https://ffmpeg.org/download.html"
    
    read -p "FFmpeg está instalado? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Por favor, instale FFmpeg primeiro."
        exit 1
    fi
fi

echo "✅ FFmpeg encontrado: $(ffmpeg -version | head -n1)"

# Criar ambiente virtual se não existir
if [ ! -d "venv" ]; then
    echo "📦 Criando ambiente virtual..."
    python3 -m venv venv
    echo "✅ Ambiente virtual criado"
else
    echo "✅ Ambiente virtual já existe"
fi

# Ativar ambiente virtual
echo "🔄 Ativando ambiente virtual..."
source venv/bin/activate

# Atualizar pip
echo "📦 Atualizando pip..."
pip install --upgrade pip

# Instalar dependências
echo "📦 Instalando dependências Python..."
echo "⚠️  Isso pode demorar alguns minutos (PyTorch é um pacote grande)..."
pip install -r requirements.txt

# Verificar instalação
echo "🔍 Verificando instalação..."
python3 -c "import torch; print('✅ PyTorch instalado:', torch.__version__)"
python3 -c "import demucs; print('✅ Demucs instalado')"
python3 -c "import fastapi; print('✅ FastAPI instalado')"
python3 -c "from pydub import AudioSegment; print('✅ pydub instalado')"

echo ""
echo "🎉 Configuração concluída com sucesso!"
echo ""
echo "Para iniciar a aplicação:"
echo "  1. Ative o ambiente virtual: source venv/bin/activate"
echo "  2. Execute: python main.py"
echo "  3. Acesse: http://localhost:8000"
echo ""
echo "Primeira execução irá baixar o modelo Demucs (~1GB)"

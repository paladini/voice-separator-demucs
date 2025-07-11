# 🚀 Início Rápido - Voice Separator

Guia de 5 minutos para usar o separador de vocais.

## 🐳 Opção 1: Docker (Mais Fácil)

Se você tem Docker instalado:

```bash
# Download e executar
docker run -p 8000:8000 voice-separator

# Acesse: http://localhost:8000
```

**Pronto!** Pule para "Como usar" abaixo.

## 🐍 Opção 2: Python

**Pré-requisitos:**
- Python 3.8+
- FFmpeg instalado

```bash
# 1. Instalar FFmpeg
sudo apt-get install ffmpeg  # Ubuntu/Debian
# ou
brew install ffmpeg  # macOS

# 2. Entrar na pasta do projeto
cd voice-separator-demucs

# 3. Instalar dependências  
pip install -r requirements.txt

# 4. Executar
python main.py

# Acesse: http://localhost:8000
```

## 🎵 Como usar

### Upload de Arquivo
1. **Selecione elementos** (vocais, bateria, baixo, etc.)
2. **Escolha arquivo** de áudio (MP3, WAV, etc.)
3. **Clique "Separar"**
4. **Aguarde** 2-5 minutos
5. **Baixe** os resultados

### YouTube
1. **Selecione elementos** desejados
2. **Cole URL** do YouTube
3. **Clique "Baixar e Separar"**
4. **Aguarde** download + processamento
5. **Baixe** os arquivos separados

## ⚡ Dicas rápidas

- **Primeira vez:** O modelo será baixado (~200MB)
- **Apenas vocais:** Mais rápido (~2 min)
- **Todos elementos:** Mais lento (~5 min)
- **YouTube:** Máximo 10 minutos de vídeo

## 📋 Formatos aceitos

✅ **MP3**, WAV, FLAC, M4A, AAC  
📏 **Limite:** 100MB por arquivo  
⏱️ **YouTube:** Máximo 10 minutos

## 🆘 Problemas?

**"FFmpeg não encontrado"**
```bash
# Ubuntu/Debian
sudo apt-get install ffmpeg

# macOS
brew install ffmpeg
```

**Processamento muito lento**
- Use arquivos menores
- Feche outros programas
- Selecione menos elementos

**Erro ao baixar do YouTube**
- Verifique se o vídeo é público
- Máximo 10 minutos de duração

---

�‍💻 **Desenvolvido por:** [Fernando Paladini](https://github.com/paladini)  
�📖 **Para mais detalhes:** [README.md](README.md)

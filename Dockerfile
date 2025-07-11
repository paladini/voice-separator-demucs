# Dockerfile para Voice Separator by Fernando Paladini
# GitHub: https://github.com/paladini
FROM python:3.9-slim

# Metadata
LABEL maintainer="Fernando Paladini <fernando@paladini.dev>"
LABEL description="Voice Separator - Separação de vocais usando Demucs"
LABEL version="1.0.0"

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Criar diretório de trabalho
WORKDIR /app

# Copiar requirements primeiro para cache de layers
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY . .

# Criar diretório de output
RUN mkdir -p static/output

# Expor porta
EXPOSE 8000

# Comando para iniciar a aplicação
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

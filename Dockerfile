# Multi-stage build para reduzir tamanho
FROM python:3.9-slim AS builder

# Instalar dependências de build
RUN apt-get update && apt-get upgrade -y && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependências Python em ambiente virtual
COPY requirements.txt .
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Estágio final - imagem limpa
FROM python:3.9-slim

# Atualizar pacotes para mitigar vulnerabilidades
RUN apt-get update && apt-get upgrade -y && rm -rf /var/lib/apt/lists/*

# Metadata
LABEL maintainer="Fernando Paladini <fernando@paladini.dev>"
LABEL description="Voice Separator - Separação de vocais usando Demucs"
LABEL version="1.0.0"

# Instalar apenas dependências de runtime
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copiar ambiente virtual do builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Remover criação de usuário - rodar como root para evitar problemas de permissão

# Criar diretório de trabalho
WORKDIR /app

# Copiar código da aplicação
COPY . .

# Criar diretório de output e cache para modelos
RUN mkdir -p static/output && \
    mkdir -p /root/.cache/torch/hub && \
    chmod 777 static/output

# Definir variável de ambiente para cache
ENV TORCH_HOME=/root/.cache/torch

# Expor porta
EXPOSE 8000

# Volumes para persistir dados
VOLUME ["/root/.cache", "/app/static/output"]

# Comando para iniciar a aplicação
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

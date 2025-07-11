import os
import tempfile
from pathlib import Path
from typing import List, Optional
from fastapi import FastAPI, File, UploadFile, HTTPException, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Criar instância do FastAPI
app = FastAPI(
    title="Voice Separator by Fernando Paladini", 
    description="Separação de vocais usando Demucs",
    version="1.0.0",
    contact={
        "name": "Fernando Paladini",
        "url": "https://github.com/paladini",
    }
)

# Criar diretório de saída se não existir (relativo à raiz do projeto)
project_root = Path(__file__).parent.parent.parent
output_dir = project_root / "static" / "output"
output_dir.mkdir(parents=True, exist_ok=True)

# Montar arquivos estáticos
app.mount("/static", StaticFiles(directory=str(project_root / "static")), name="static")

# Configurar templates
templates = Jinja2Templates(directory=str(project_root / "templates"))

# Formatos de áudio aceitos
ALLOWED_AUDIO_FORMATS = {
    "audio/mpeg",  # MP3
    "audio/wav",   # WAV
    "audio/x-wav", # WAV alternativo
    "audio/flac",  # FLAC
    "audio/mp4",   # M4A
    "audio/aac",   # AAC
}

# Extensões de arquivo aceitas
ALLOWED_EXTENSIONS = {".mp3", ".wav", ".flac", ".m4a", ".aac"}


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Página principal da aplicação"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api/stems")
async def get_available_stems():
    """
    Endpoint para obter informações sobre os stems disponíveis.
    
    Returns:
        JSON com informações dos stems disponíveis
    """
    from src.core import AVAILABLE_STEMS, AudioSeparator
    
    return {
        "success": True,
        "stems": AVAILABLE_STEMS,
        "default_selection": ["vocals"],
        "recommendations": {
            "fast": ["vocals"],
            "karaoke": ["vocals", "instrumental"],
            "full": ["drums", "bass", "other", "vocals"]
        }
    }


@app.post("/api/separate")
async def separate_audio(
    file: UploadFile = File(...),
    stems: str = Form(default="vocals")  # String com stems separados por vírgula
):
    """
    Endpoint para upload e separação de áudio com seleção de stems.
    
    Args:
        file: Arquivo de áudio enviado pelo usuário
        stems: String com stems separados por vírgula (ex: "vocals,instrumental")
        
    Returns:
        JSON com URLs para download dos arquivos processados
    """
    try:
        # Importar depois de garantir que o módulo está disponível
        from src.core import separate_audio as core_separate_audio, AVAILABLE_STEMS, get_audio_separator
        
        # Validar tipo de arquivo
        if file.content_type not in ALLOWED_AUDIO_FORMATS:
            # Verificar também pela extensão como fallback
            file_extension = Path(file.filename).suffix.lower()
            if file_extension not in ALLOWED_EXTENSIONS:
                raise HTTPException(
                    status_code=400,
                    detail=f"Formato de arquivo não suportado. Use: {', '.join(ALLOWED_EXTENSIONS)}"
                )
        
        # Verificar tamanho do arquivo (limite de 100MB)
        if hasattr(file, 'size') and file.size > 100 * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail="Arquivo muito grande. Limite máximo: 100MB"
            )
        
        # Processar lista de stems
        selected_stems = [stem.strip() for stem in stems.split(",") if stem.strip()]
        if not selected_stems:
            selected_stems = ["vocals"]  # Padrão
        
        # Validar stems
        invalid_stems = [stem for stem in selected_stems if stem not in AVAILABLE_STEMS]
        if invalid_stems:
            raise HTTPException(
                status_code=400,
                detail=f"Stems inválidos: {invalid_stems}. Disponíveis: {list(AVAILABLE_STEMS.keys())}"
            )
        
        logger.info(f"Processando arquivo: {file.filename} com stems: {selected_stems}")
        
        # Obter separador singleton
        separator = get_audio_separator()
        
        # Estimar tempo de processamento
        processing_time = separator.estimate_processing_time(selected_stems)
        logger.info(f"Tempo estimado de processamento: {processing_time}")
        
        # Criar arquivo temporário
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as temp_file:
            try:
                # Salvar arquivo enviado no arquivo temporário
                content = await file.read()
                temp_file.write(content)
                temp_file.flush()
                
                temp_file_path = temp_file.name
                
                logger.info("Arquivo salvo temporariamente, iniciando separação...")
                
                # Processar separação de áudio usando o separador
                result_paths = separator.separate_stems(temp_file_path, selected_stems)
                
                logger.info("Separação concluída com sucesso!")
                
                # Construir resposta
                base_url = "/"
                files_data = {}
                
                for stem, path in result_paths.items():
                    stem_info = AVAILABLE_STEMS[stem]
                    files_data[stem] = {
                        "url": f"{base_url}{path}",
                        "filename": Path(path).name,
                        "name": stem_info["name"],
                        "icon": stem_info["icon"]
                    }
                
                return {
                    "success": True,
                    "message": "Separação concluída com sucesso!",
                    "files": files_data,
                    "processing_time": processing_time,
                    "stems_processed": selected_stems
                }
                
            finally:
                # Limpar arquivo temporário
                try:
                    os.unlink(temp_file_path)
                    logger.info("Arquivo temporário removido")
                except OSError as e:
                    logger.warning(f"Erro ao remover arquivo temporário: {e}")
                    
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Erro durante processamento: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno do servidor: {str(e)}"
        )


@app.post("/api/separate-youtube")
async def separate_youtube_audio(
    url: str = Form(...),
    stems: str = Form(default="vocals")  # String com stems separados por vírgula
):
    """
    Endpoint para download e separação de áudio do YouTube com seleção de stems.
    
    Args:
        url: URL do vídeo do YouTube
        stems: String com stems separados por vírgula (ex: "vocals,instrumental")
        
    Returns:
        JSON com URLs para download dos arquivos processados
    """
    try:
        # Importar depois de garantir que o módulo está disponível
        from src.core import (
            separate_audio as core_separate_audio, 
            download_youtube_audio, 
            AVAILABLE_STEMS, 
            get_audio_separator,
            YouTubeDownloader
        )
        
        # Criar instância do downloader
        youtube_downloader = YouTubeDownloader()
        
        # Validar URL
        if not youtube_downloader.validate_youtube_url(url):
            raise HTTPException(
                status_code=400,
                detail="URL do YouTube inválida. Use links como: https://www.youtube.com/watch?v=..."
            )
        
        # Processar lista de stems
        selected_stems = [stem.strip() for stem in stems.split(",") if stem.strip()]
        if not selected_stems:
            selected_stems = ["vocals"]  # Padrão
        
        # Validar stems
        invalid_stems = [stem for stem in selected_stems if stem not in AVAILABLE_STEMS]
        if invalid_stems:
            raise HTTPException(
                status_code=400,
                detail=f"Stems inválidos: {invalid_stems}. Disponíveis: {list(AVAILABLE_STEMS.keys())}"
            )
        
        logger.info(f"Processando URL do YouTube: {url} com stems: {selected_stems}")
        
        # Obter separador singleton
        separator = get_audio_separator()
        
        # Obter informações do vídeo primeiro
        video_info = youtube_downloader.get_video_info(url)
        if not video_info:
            raise HTTPException(
                status_code=400,
                detail="Não foi possível acessar o vídeo. Verifique se é público e acessível."
            )
        
        # Verificar duração (limite de 10 minutos)
        if video_info['duration'] > 600:
            raise HTTPException(
                status_code=400,
                detail=f"Vídeo muito longo ({video_info['duration']//60}:{video_info['duration']%60:02d}). Limite: 10 minutos."
            )
        
        # Estimar tempo de processamento
        processing_time = separator.estimate_processing_time(selected_stems)
        logger.info(f"Tempo estimado de processamento: {processing_time}")
        
        logger.info(f"Baixando áudio: {video_info['title']}")
        
        # Baixar áudio do YouTube
        temp_audio_path, video_data = download_youtube_audio(url)
        
        try:
            logger.info("Arquivo baixado, iniciando separação...")
            
            # Processar separação de áudio usando o separador criado
            result_paths = separator.separate_stems(temp_audio_path, selected_stems)
            
            logger.info("Separação concluída com sucesso!")
            
            # Construir resposta
            base_url = "/"
            files_data = {}
            
            for stem, path in result_paths.items():
                stem_info = AVAILABLE_STEMS[stem]
                files_data[stem] = {
                    "url": f"{base_url}{path}",
                    "filename": Path(path).name,
                    "name": stem_info["name"],
                    "icon": stem_info["icon"]
                }
            
            return {
                "success": True,
                "message": "Separação concluída com sucesso!",
                "files": files_data,
                "processing_time": processing_time,
                "stems_processed": selected_stems,
                "video_info": video_data
            }
            
        finally:
            # Limpar arquivo temporário do YouTube
            youtube_downloader.cleanup_file(temp_audio_path)
            
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Erro durante processamento do YouTube: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno do servidor: {str(e)}"
        )


@app.get("/health")
async def health_check():
    """Endpoint de verificação de saúde da aplicação"""
    return {"status": "healthy", "message": "Voice Separator API is running"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

import os
import tempfile
import uuid
from pathlib import Path
from typing import Optional, Tuple
import yt_dlp
import logging

logger = logging.getLogger(__name__)


class YouTubeDownloader:
    def __init__(self, temp_dir: str = None):
        self.temp_dir = Path(temp_dir) if temp_dir else Path(tempfile.gettempdir())
        
        # Configuração ULTRA OTIMIZADA do yt-dlp para VELOCIDADE MÁXIMA
        self.ydl_opts = {
            # Formato mais rápido: baixar diretamente stream de áudio
            'format': 'bestaudio[ext=m4a]/bestaudio[ext=webm]/bestaudio/best',
            
            # Configurações de velocidade
            'concurrent_fragments': 8,  # Download paralelo de fragmentos
            'retries': 3,  # Menos tentativas para falhar mais rápido
            'fragment_retries': 2,
            'buffersize': 16384,  # Buffer maior
            'http_chunk_size': 1048576,  # 1MB chunks
            
            # Pular processamento desnecessário
            'extractaudio': False,  # NÃO extrair áudio aqui (fazer depois)
            'postprocessors': [],  # Sem pós-processamento
            'embed_subs': False,
            'writesubtitles': False,
            'writeautomaticsub': False,
            'writethumbnail': False,
            'writeinfojson': False,
            'writedescription': False,
            'writeannotations': False,
            
            # Configurações de arquivo
            'outtmpl': str(self.temp_dir / '%(id)s.%(ext)s'),  # Nome mais simples
            'restrictfilenames': True,
            'noplaylist': True,
            'no_warnings': True,
            'quiet': True,
            
            # Limites para velocidade
            'socket_timeout': 10,
            'prefer_ffmpeg': True,  # Usar ffmpeg se disponível
        }

    def validate_youtube_url(self, url: str) -> bool:
        """
        Valida se a URL é um link válido do YouTube.
        
        Args:
            url: URL para validar
            
        Returns:
            True se for uma URL válida do YouTube
        """
        youtube_domains = [
            'youtube.com', 'youtu.be', 'www.youtube.com', 
            'm.youtube.com', 'music.youtube.com'
        ]
        
        try:
            # Verificação básica de domínio
            for domain in youtube_domains:
                if domain in url.lower():
                    return True
            return False
        except Exception:
            return False

    def get_video_info(self, url: str) -> Optional[dict]:
        """
        Obtém informações do vídeo sem baixar.
        
        Args:
            url: URL do YouTube
            
        Returns:
            Dicionário com informações do vídeo ou None se houver erro
        """
        try:
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(url, download=False)
                
                # Verificar duração (limite de 10 minutos para otimização)
                duration = info.get('duration', 0)
                if duration > 600:  # 10 minutos
                    logger.warning(f"Vídeo muito longo: {duration}s")
                
                return {
                    'title': info.get('title', 'Unknown'),
                    'duration': duration,
                    'uploader': info.get('uploader', 'Unknown'),
                    'view_count': info.get('view_count', 0),
                    'id': info.get('id', ''),
                }
        except Exception as e:
            logger.error(f"Erro ao obter informações do vídeo: {e}")
            return None

    def download_audio(self, url: str) -> Tuple[str, dict]:
        """
        Baixa o áudio de um vídeo do YouTube RAPIDAMENTE.
        
        Args:
            url: URL do YouTube
            
        Returns:
            Tuple com (caminho_do_arquivo, informações_do_video)
            
        Raises:
            Exception: Se houver erro no download
        """
        if not self.validate_youtube_url(url):
            raise ValueError("URL do YouTube inválida")
        
        # Obter informações do vídeo primeiro (mais rápido)
        video_info = self.get_video_info(url)
        if not video_info:
            raise Exception("Não foi possível obter informações do vídeo")
        
        # Verificar duração (limite de 10 minutos)
        if video_info['duration'] > 600:
            raise Exception(f"Vídeo muito longo ({video_info['duration']}s). Limite: 10 minutos")
        
        try:
            logger.info(f"🚀 Download RÁPIDO: {video_info['title']}")
            
            # Gerar nome único SIMPLES para o arquivo
            unique_id = str(uuid.uuid4())[:8]
            video_id = video_info.get('id', unique_id)
            
            # Configurar opções específicas para VELOCIDADE MÁXIMA
            ydl_opts = self.ydl_opts.copy()
            ydl_opts['outtmpl'] = str(self.temp_dir / f"{video_id}.%(ext)s")
            
            downloaded_file = None
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                logger.info("⚡ Iniciando download otimizado...")
                
                # Download DIRETO sem processamento extra
                info = ydl.extract_info(url, download=True)
                actual_filename = ydl.prepare_filename(info)
                
                if os.path.exists(actual_filename):
                    downloaded_file = actual_filename
                else:
                    # Procurar arquivo baixado por extensões comuns
                    for ext in ['m4a', 'webm', 'mp4', 'wav', 'mp3']:
                        potential_file = self.temp_dir / f"{video_id}.{ext}"
                        if potential_file.exists():
                            downloaded_file = str(potential_file)
                            break
                
                if not downloaded_file:
                    raise Exception("Arquivo baixado não encontrado")
                
                # Se não for um formato de áudio direto, converter RAPIDAMENTE
                if not downloaded_file.lower().endswith(('.mp3', '.wav', '.m4a', '.aac')):
                    logger.info("🔄 Conversão rápida para WAV...")
                    converted_file = str(self.temp_dir / f"{video_id}_converted.wav")
                    
                    # Usar pydub para conversão rápida
                    from pydub import AudioSegment
                    audio = AudioSegment.from_file(downloaded_file)
                    audio.export(converted_file, format="wav")
                    
                    # Remover arquivo original e usar convertido
                    os.unlink(downloaded_file)
                    downloaded_file = converted_file
                
                logger.info(f"✅ Download concluído: {os.path.basename(downloaded_file)}")
                return downloaded_file, video_info
                
        except Exception as e:
            logger.error(f"❌ Erro no download: {e}")
            raise Exception(f"Erro ao baixar áudio do YouTube: {str(e)}")

    def cleanup_file(self, file_path: str):
        """
        Remove arquivo temporário.
        
        Args:
            file_path: Caminho do arquivo para remover
        """
        try:
            if os.path.exists(file_path):
                os.unlink(file_path)
                logger.info(f"Arquivo temporário removido: {file_path}")
        except Exception as e:
            logger.warning(f"Erro ao remover arquivo temporário {file_path}: {e}")


# Instância global
youtube_downloader = YouTubeDownloader()


def download_youtube_audio(url: str) -> Tuple[str, dict]:
    """
    Função de conveniência para baixar áudio do YouTube.
    
    Args:
        url: URL do YouTube
        
    Returns:
        Tuple com (caminho_do_arquivo, informações_do_video)
    """
    return youtube_downloader.download_audio(url)

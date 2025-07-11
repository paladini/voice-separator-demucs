"""
Módulo principal do Voice Separator.

Este módulo contém as classes e funções principais para:
- Separação de áudio usando Demucs
- Download de áudio do YouTube
- Processamento de stems individuais
"""

from .separator import (
    AudioSeparator, 
    get_audio_separator,
    separate_audio, 
    separate_vocals,
    AVAILABLE_STEMS
)
from .youtube_downloader import (
    YouTubeDownloader,
    download_youtube_audio
)

__all__ = [
    'AudioSeparator',
    'get_audio_separator',
    'separate_audio', 
    'separate_vocals',
    'AVAILABLE_STEMS',
    'YouTubeDownloader',
    'download_youtube_audio'
]

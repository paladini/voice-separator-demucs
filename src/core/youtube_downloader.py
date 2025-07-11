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
        
        # ULTRA OPTIMIZED yt-dlp configuration for MAXIMUM SPEED
        self.ydl_opts = {
            # Fastest format: download audio stream directly
            'format': 'bestaudio[ext=m4a]/bestaudio[ext=webm]/bestaudio/best',
            
            # Speed settings
            'concurrent_fragments': 8,  # Parallel fragment download
            'retries': 3,  # Fewer retries to fail faster
            'fragment_retries': 2,
            'buffersize': 16384,  # Larger buffer
            'http_chunk_size': 1048576,  # 1MB chunks
            
            # Skip unnecessary processing
            'extractaudio': False,  # DON'T extract audio here (do it later)
            'postprocessors': [],  # No post-processing
            'embed_subs': False,
            'writesubtitles': False,
            'writeautomaticsub': False,
            'writethumbnail': False,
            'writeinfojson': False,
            'writedescription': False,
            'writeannotations': False,
            
            # File settings
            'outtmpl': str(self.temp_dir / '%(id)s.%(ext)s'),  # Simpler name
            'restrictfilenames': True,
            'noplaylist': True,
            'no_warnings': True,
            'quiet': True,
            
            # Speed limits
            'socket_timeout': 10,
            'prefer_ffmpeg': True,  # Use ffmpeg if available
        }

    def validate_youtube_url(self, url: str) -> bool:
        """
        Validates if the URL is a valid YouTube link.
        
        Args:
            url: URL to validate
            
        Returns:
            True if it's a valid YouTube URL
        """
        youtube_domains = [
            'youtube.com', 'youtu.be', 'www.youtube.com', 
            'm.youtube.com', 'music.youtube.com'
        ]
        
        try:
            # Basic domain verification
            for domain in youtube_domains:
                if domain in url.lower():
                    return True
            return False
        except Exception:
            return False

    def get_video_info(self, url: str) -> Optional[dict]:
        """
        Gets video information without downloading.
        
        Args:
            url: YouTube URL
            
        Returns:
            Dictionary with video information or None if error
        """
        try:
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(url, download=False)
                
                # Check duration (10 minute limit for optimization)
                duration = info.get('duration', 0)
                if duration > 600:  # 10 minutes
                    logger.warning(f"Video too long: {duration}s")
                
                return {
                    'title': info.get('title', 'Unknown'),
                    'duration': duration,
                    'uploader': info.get('uploader', 'Unknown'),
                    'view_count': info.get('view_count', 0),
                    'id': info.get('id', ''),
                }
        except Exception as e:
            logger.error(f"Error getting video information: {e}")
            return None

    def download_audio(self, url: str) -> Tuple[str, dict]:
        """
        Downloads audio from a YouTube video QUICKLY.
        
        Args:
            url: YouTube URL
            
        Returns:
            Tuple with (file_path, video_info)
            
        Raises:
            Exception: If there's an error in the download
        """
        if not self.validate_youtube_url(url):
            raise ValueError("Invalid YouTube URL")
        
        # Get video information first (faster)
        video_info = self.get_video_info(url)
        if not video_info:
            raise Exception("Could not get video information")
        
        # Check duration (10 minute limit)
        if video_info['duration'] > 600:
            raise Exception(f"Video too long ({video_info['duration']}s). Limit: 10 minutes")
        
        try:
            logger.info(f"🚀 FAST Download: {video_info['title']}")
            
            # Generate SIMPLE unique filename
            unique_id = str(uuid.uuid4())[:8]
            video_id = video_info.get('id', unique_id)
            
            # Configure specific options for MAXIMUM SPEED
            ydl_opts = self.ydl_opts.copy()
            ydl_opts['outtmpl'] = str(self.temp_dir / f"{video_id}.%(ext)s")
            
            downloaded_file = None
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                logger.info("⚡ Starting optimized download...")
                
                # DIRECT download without extra processing
                info = ydl.extract_info(url, download=True)
                actual_filename = ydl.prepare_filename(info)
                
                if os.path.exists(actual_filename):
                    downloaded_file = actual_filename
                else:
                    # Search for downloaded file by common extensions
                    for ext in ['m4a', 'webm', 'mp4', 'wav', 'mp3']:
                        potential_file = self.temp_dir / f"{video_id}.{ext}"
                        if potential_file.exists():
                            downloaded_file = str(potential_file)
                            break
                
                if not downloaded_file:
                    raise Exception("Downloaded file not found")
                
                # If not a direct audio format, convert QUICKLY
                if not downloaded_file.lower().endswith(('.mp3', '.wav', '.m4a', '.aac')):
                    logger.info("🔄 Quick conversion to WAV...")
                    converted_file = str(self.temp_dir / f"{video_id}_converted.wav")
                    
                    # Use pydub for quick conversion
                    from pydub import AudioSegment
                    audio = AudioSegment.from_file(downloaded_file)
                    audio.export(converted_file, format="wav")
                    
                    # Remove original file and use converted one
                    os.unlink(downloaded_file)
                    downloaded_file = converted_file
                
                logger.info(f"✅ Download completed: {os.path.basename(downloaded_file)}")
                return downloaded_file, video_info
                
        except Exception as e:
            logger.error(f"❌ Download error: {e}")
            raise Exception(f"Error downloading audio from YouTube: {str(e)}")

    def cleanup_file(self, file_path: str):
        """
        Removes temporary file.
        
        Args:
            file_path: Path of the file to remove
        """
        try:
            if os.path.exists(file_path):
                os.unlink(file_path)
                logger.info(f"Temporary file removed: {file_path}")
        except Exception as e:
            logger.warning(f"Error removing temporary file {file_path}: {e}")


# Global instance
youtube_downloader = YouTubeDownloader()


def download_youtube_audio(url: str) -> Tuple[str, dict]:
    """
    Convenience function to download audio from YouTube.
    
    Args:
        url: YouTube URL
        
    Returns:
        Tuple with (file_path, video_info)
    """
    return youtube_downloader.download_audio(url)

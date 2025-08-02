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

# Create FastAPI instance
app = FastAPI(
    title="Voice Separator by Fernando Paladini", 
    description="Voice separation using Demucs",
    version="1.0.0",
    contact={
        "name": "Fernando Paladini",
        "url": "https://github.com/paladini",
    }
)

# Create output directory if it doesn't exist (relative to project root)
project_root = Path(__file__).parent.parent.parent
output_dir = project_root / "static" / "output"
output_dir.mkdir(parents=True, exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory=str(project_root / "static")), name="static")

# Configure templates
templates = Jinja2Templates(directory=str(project_root / "templates"))

# Accepted audio formats
ALLOWED_AUDIO_FORMATS = {
    "audio/mpeg",  # MP3
    "audio/wav",   # WAV
    "audio/x-wav", # WAV alternative
    "audio/flac",  # FLAC
    "audio/mp4",   # M4A
    "audio/aac",   # AAC
}

# Accepted file extensions
ALLOWED_EXTENSIONS = {".mp3", ".wav", ".flac", ".m4a", ".aac"}


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Main application page"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api/stems")
async def get_available_stems():
    """
    Endpoint to get information about available stems.
    
    Returns:
        JSON with available stems information
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
    stems: str = Form(default="vocals"),  # String with stems separated by comma
    model: str = Form(default="mdx_extra_q")
):
    """
    Endpoint for audio upload and separation with stem selection.
    
    Args:
        file: Audio file sent by user
        stems: String with stems separated by comma (ex: "vocals,instrumental")
        
    Returns:
        JSON with URLs for downloading processed files
    """
    try:
        # Import after ensuring module is available
        from src.core import separate_audio as core_separate_audio, AVAILABLE_STEMS, get_audio_separator
        # Supported models
        SUPPORTED_MODELS = ["mdx_extra_q", "mdx", "htdemucs", "htdemucs_ft"]
        if model not in SUPPORTED_MODELS:
            raise HTTPException(status_code=400, detail=f"Invalid model: {model}. Supported: {SUPPORTED_MODELS}")
        
        # Validate file type
        if file.content_type not in ALLOWED_AUDIO_FORMATS:
            # Also check by extension as fallback
            file_extension = Path(file.filename).suffix.lower()
            if file_extension not in ALLOWED_EXTENSIONS:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported file format. Use: {', '.join(ALLOWED_EXTENSIONS)}"
                )
        
        # Process stems list
        selected_stems = [stem.strip() for stem in stems.split(",") if stem.strip()]
        if not selected_stems:
            selected_stems = ["vocals"]  # Default
        
        # Validate stems
        invalid_stems = [stem for stem in selected_stems if stem not in AVAILABLE_STEMS]
        if invalid_stems:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid stems: {invalid_stems}. Available: {list(AVAILABLE_STEMS.keys())}"
            )
        
        logger.info(f"Processing file: {file.filename} with stems: {selected_stems}")
        
        # Get singleton separator
        try:
            separator = get_audio_separator(model)
        except Exception as e:
            logger.error(f"Model/device error: {e}")
            raise HTTPException(status_code=400, detail=str(e))
        
        # Estimate processing time
        processing_time = separator.estimate_processing_time(selected_stems)
        logger.info(f"Estimated processing time: {processing_time}")
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as temp_file:
            try:
                # Save uploaded file to temporary file
                content = await file.read()
                temp_file.write(content)
                temp_file.flush()
                
                temp_file_path = temp_file.name
                
                logger.info("File saved temporarily, starting separation...")
                
                # Process audio separation using the separator
                result_paths = separator.separate_stems(temp_file_path, selected_stems)
                
                logger.info("Separation completed successfully!")
                
                # Build response
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
                    "message": "Separation completed successfully!",
                    "files": files_data,
                    "processing_time": processing_time,
                    "stems_processed": selected_stems
                }
                
            finally:
                # Clean up temporary file
                try:
                    os.unlink(temp_file_path)
                    logger.info("Temporary file removed")
                except OSError as e:
                    logger.warning(f"Error removing temporary file: {e}")
                    
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error during processing: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@app.post("/api/separate-youtube")
async def separate_youtube_audio(
    url: str = Form(...),
    stems: str = Form(default="vocals"),  # String with stems separated by comma
    model: str = Form(default="mdx_extra_q")
):
    """
    Endpoint for YouTube audio download and separation with stem selection.
    
    Args:
        url: YouTube video URL
        stems: String with stems separated by comma (ex: "vocals,instrumental")
        
    Returns:
        JSON with URLs for downloading processed files
    """
    try:
        # Import after ensuring module is available
        from src.core import (
            separate_audio as core_separate_audio, 
            download_youtube_audio, 
            AVAILABLE_STEMS, 
            get_audio_separator,
            YouTubeDownloader
        )
        SUPPORTED_MODELS = ["mdx_extra_q", "mdx", "htdemucs", "htdemucs_ft"]
        if model not in SUPPORTED_MODELS:
            raise HTTPException(status_code=400, detail=f"Invalid model: {model}. Supported: {SUPPORTED_MODELS}")
        
        # Create downloader instance
        youtube_downloader = YouTubeDownloader()
        
        # Validate URL
        if not youtube_downloader.validate_youtube_url(url):
            raise HTTPException(
                status_code=400,
                detail="Invalid YouTube URL. Use links like: https://www.youtube.com/watch?v=..."
            )
        
        # Process stems list
        selected_stems = [stem.strip() for stem in stems.split(",") if stem.strip()]
        if not selected_stems:
            selected_stems = ["vocals"]  # Default
        
        # Validate stems
        invalid_stems = [stem for stem in selected_stems if stem not in AVAILABLE_STEMS]
        if invalid_stems:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid stems: {invalid_stems}. Available: {list(AVAILABLE_STEMS.keys())}"
            )
        
        logger.info(f"Processing YouTube URL: {url} with stems: {selected_stems}")
        
        # Get singleton separator
        try:
            separator = get_audio_separator(model)
        except Exception as e:
            logger.error(f"Model/device error: {e}")
            raise HTTPException(status_code=400, detail=str(e))
        
        # Get video information first
        video_info = youtube_downloader.get_video_info(url)
        if not video_info:
            raise HTTPException(
                status_code=400,
                detail="Could not access video. Check if it's public and accessible."
            )
        
        # Check duration (10 minute limit)
        if video_info['duration'] > 600:
            raise HTTPException(
                status_code=400,
                detail=f"Video too long ({video_info['duration']//60}:{video_info['duration']%60:02d}). Limit: 10 minutes."
            )
        
        # Estimate processing time
        processing_time = separator.estimate_processing_time(selected_stems)
        logger.info(f"Estimated processing time: {processing_time}")
        
        logger.info(f"Downloading audio: {video_info['title']}")
        
        # Download audio from YouTube
        temp_audio_path, video_data = download_youtube_audio(url)
        
        try:
            logger.info("File downloaded, starting separation...")
            
            # Process audio separation using the created separator
            result_paths = separator.separate_stems(temp_audio_path, selected_stems)
            
            logger.info("Separation completed successfully!")
            
            # Build response
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
                "message": "Separation completed successfully!",
                "files": files_data,
                "processing_time": processing_time,
                "stems_processed": selected_stems,
                "video_info": video_data
            }
            
        finally:
            # Clean up temporary YouTube file
            youtube_downloader.cleanup_file(temp_audio_path)
            
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error during YouTube processing: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@app.get("/health")
async def health_check():
    """Application health check endpoint"""
    return {"status": "healthy", "message": "Voice Separator API is running"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=7860,
        reload=True,
        timeout_keep_alive=1200,  # 20 minutes
        timeout_graceful_shutdown=1200,  # 20 minutes
    )

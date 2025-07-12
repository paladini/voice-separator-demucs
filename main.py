"""
Voice Separator - Main Application

This is the entry point for the Voice Separator application.
The application allows separating audio stems (vocals, drums, bass, other) 
using Meta AI's Demucs model.

Features:
- Audio file upload
- YouTube video download and processing
- Specific stem selection for optimized processing
- Modern and responsive web interface

To run:
    python main.py
    
Or use uvicorn directly:
    uvicorn main:app --host 0.0.0.0 --port 7860 --reload
"""

import sys
from pathlib import Path

# Add src directory to Python path for imports
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Import FastAPI application
from src.api import app

if __name__ == "__main__":
    import uvicorn
    
    print("🎵 Starting Voice Separator - Web Server Mode...")
    print("📁 Organized structure: src/core + src/api")
    print("🚀 Access: http://localhost:7860")
    print("📖 API Docs: http://localhost:7860/docs")
    print("🔍 Health Check: http://localhost:7860/health")
    print("💡 For desktop app, use: python desktop_app.py")
    
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=7860, 
        reload=True,
        reload_dirs=["src", "templates", "static"]
    )

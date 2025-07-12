#!/usr/bin/env python3
"""
Voice Separator - Desktop Application Entry Point

This is the desktop application entry point that runs as a Tauri sidecar.
It performs dependency checks and starts the FastAPI server on a fixed port
for the Tauri frontend to connect to.

Architecture: "Live Server" - Tauri window loads UI directly from local FastAPI server.
"""

import sys
import os
import subprocess
import importlib
import shutil
from pathlib import Path
from typing import List, Tuple, Optional

class DependencyChecker:
    """
    Handles checking and installation of all dependencies required
    for the Voice Separator desktop application.
    """
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.requirements_file = self.project_root / "requirements.txt"
        
    def check_python_version(self) -> bool:
        """Check if Python version is compatible (3.8+)"""
        version = sys.version_info
        if version.major == 3 and version.minor >= 8:
            print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
            return True
        else:
            print(f"❌ Python {version.major}.{version.minor}.{version.micro} is not compatible. Requires Python 3.8+")
            return False
    
    def check_ffmpeg(self) -> bool:
        """Check if FFmpeg is installed and accessible"""
        try:
            result = subprocess.run(
                ["ffmpeg", "-version"], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            if result.returncode == 0:
                print("✅ FFmpeg is installed and accessible")
                return True
            else:
                print("❌ FFmpeg found but not working properly")
                return False
        except FileNotFoundError:
            print("❌ FFmpeg not found in PATH")
            return False
        except subprocess.TimeoutExpired:
            print("❌ FFmpeg check timed out")
            return False
        except Exception as e:
            print(f"❌ Error checking FFmpeg: {e}")
            return False
    
    def get_missing_packages(self) -> List[str]:
        """Check which packages from requirements.txt are missing"""
        if not self.requirements_file.exists():
            print(f"❌ Requirements file not found: {self.requirements_file}")
            return []
        
        missing_packages = []
        
        with open(self.requirements_file, 'r') as f:
            requirements = f.readlines()
        
        for requirement in requirements:
            requirement = requirement.strip()
            # Skip empty lines and comments
            if not requirement or requirement.startswith('#'):
                continue
            
            # Extract package name (before any version specifiers)
            package_name = requirement.split('==')[0].split('>=')[0].split('<=')[0].split('>')[0].split('<')[0].split('[')[0].strip()
            
            try:
                importlib.import_module(package_name.replace('-', '_'))
                print(f"✅ {package_name} is available")
            except ImportError:
                print(f"❌ {package_name} is missing")
                missing_packages.append(requirement)
        
        return missing_packages
    
    def install_python_packages(self, packages: List[str]) -> bool:
        """Install missing Python packages using pip"""
        if not packages:
            return True
        
        print(f"\n📦 Installing {len(packages)} missing packages...")
        try:
            # Use pip to install packages
            cmd = [sys.executable, "-m", "pip", "install"] + packages
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print("✅ All Python packages installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install packages: {e}")
            print(f"Error output: {e.stderr}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error during package installation: {e}")
            return False
    
    def check_demucs_models(self) -> bool:
        """Check if Demucs models are available (will be downloaded on first use)"""
        try:
            import torch
            # Try to import demucs to see if it's working
            import demucs
            print("✅ Demucs is available (models will be downloaded on first use)")
            return True
        except ImportError as e:
            print(f"❌ Demucs not available: {e}")
            return False
    
    def suggest_ffmpeg_installation(self):
        """Provide platform-specific FFmpeg installation instructions"""
        print("\n🔧 FFmpeg Installation Instructions:")
        
        if sys.platform.startswith('linux'):
            print("Ubuntu/Debian: sudo apt-get install ffmpeg")
            print("Fedora/CentOS: sudo dnf install ffmpeg")
            print("Arch Linux: sudo pacman -S ffmpeg")
        elif sys.platform == 'darwin':
            print("macOS: brew install ffmpeg")
            print("(Install Homebrew first: https://brew.sh/)")
        elif sys.platform.startswith('win'):
            print("Windows: Download from https://ffmpeg.org/download.html")
            print("Add ffmpeg.exe to your PATH environment variable")
        else:
            print("Please install FFmpeg for your operating system")
            print("Visit: https://ffmpeg.org/download.html")
    
    def run_all_checks(self) -> bool:
        """
        Run all dependency checks and attempt to fix issues.
        Returns True if all dependencies are satisfied.
        """
        print("🔍 Checking Voice Separator dependencies...\n")
        
        # Check Python version
        if not self.check_python_version():
            return False
        
        # Check Python packages
        missing_packages = self.get_missing_packages()
        if missing_packages:
            if not self.install_python_packages(missing_packages):
                return False
        
        # Check FFmpeg
        ffmpeg_ok = self.check_ffmpeg()
        if not ffmpeg_ok:
            self.suggest_ffmpeg_installation()
            print("\n⚠️  Please install FFmpeg and try again.")
            return False
        
        # Check Demucs (after Python packages are installed)
        if not self.check_demucs_models():
            return False
        
        print("\n✅ All dependencies are satisfied!")
        return True


def start_fastapi_server():
    """
    Start the FastAPI server on the fixed port 7860 for Tauri to connect to.
    """
    print("\n🚀 Starting FastAPI server for desktop application...")
    
    # Add src directory to Python path for imports
    src_path = Path(__file__).parent / "src"
    sys.path.insert(0, str(src_path))
    
    try:
        # Import the FastAPI app
        from src.api import app
        import uvicorn
        
        print("📡 Server starting on http://127.0.0.1:7860")
        print("🖥️  Tauri window will connect to this server")
        
        # Start server with fixed configuration for desktop app
        uvicorn.run(
            app, 
            host="127.0.0.1", 
            port=7860,
            log_level="info"
        )
        
    except ImportError as e:
        print(f"❌ Failed to import FastAPI app: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    """
    Main entry point for the desktop application.
    
    This script:
    1. Checks all dependencies (Python packages, FFmpeg, Demucs)
    2. Installs missing Python packages if needed
    3. Starts the FastAPI server on port 7860
    4. The Tauri frontend will connect to this server
    """
    
    print("🎵 Voice Separator - Desktop Application")
    print("=" * 50)
    
    # Initialize dependency checker
    checker = DependencyChecker()
    
    # Run all dependency checks
    if not checker.run_all_checks():
        print("\n❌ Dependency checks failed. Please resolve the issues above and try again.")
        sys.exit(1)
    
    # If all checks pass, start the server
    start_fastapi_server()

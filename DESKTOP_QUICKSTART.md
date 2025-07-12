# 🖥️ Voice Separator - Desktop Application Quick Start

This guide will help you build and run the Voice Separator as a native desktop application using Tauri.

## 📋 Architecture Overview

The desktop application uses a **"Live Server"** architecture:
- **No frontend build step** required
- **Single codebase** for both web and desktop versions  
- **Tauri window** loads UI directly from local FastAPI server
- **Python backend** runs as a sidecar process
- **Unified development workflow**

```
┌─────────────────┐    HTTP Requests    ┌──────────────────┐
│   Tauri Window  │ ◄─────────────────► │  Python FastAPI │
│ (Frontend UI)   │  127.0.0.1:7860     │   (Backend)      │
└─────────────────┘                     └──────────────────┘
```

## 🔧 Prerequisites

### 1. System Dependencies
- **Python 3.8+** (already required for the web version)
- **FFmpeg** (already required for the web version)
- **Rust** (for Tauri compilation)
- **Node.js 16+** (for Tauri CLI)

### 2. Install Rust
```bash
# Install Rust (if not already installed)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source ~/.cargo/env

# Verify installation
rustc --version
cargo --version
```

### 3. Install System Dependencies

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install libwebkit2gtk-4.1-dev \
  build-essential \
  curl \
  wget \
  file \
  libxdo-dev \
  libssl-dev \
  libayatana-appindicator3-dev \
  librsvg2-dev
```

**Fedora:**
```bash
sudo dnf check-update
sudo dnf install webkit2gtk4.1-devel \
  openssl-devel \
  curl \
  wget \
  file \
  libappindicator-gtk3-devel \
  librsvg2-devel
```

**Arch Linux:**
```bash
sudo pacman -Syu
sudo pacman -S webkit2gtk-4.1 \
  base-devel \
  curl \
  wget \
  file \
  openssl \
  libayatana-appindicator \
  librsvg
```

### 5. Install Node.js
```bash
# Ubuntu/Debian
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt-get install -y nodejs

# macOS (using Homebrew)
brew install node

# Verify installation
node --version
npm --version
```

### 6. Install Tauri CLI
```bash
# Navigate to desktop directory
cd desktop/

# Install Tauri CLI (v2.0)
npm install

# Verify Tauri installation
npx tauri --version
```

## 🚀 Development Workflow

### Quick Start (Recommended)

**Step 1: Start the Python backend first**
```bash
# From project root
python desktop_app.py
# Wait for "📡 Server starting on http://127.0.0.1:7860" message
```

**Step 2: In a new terminal, start Tauri**
```bash
# From the desktop/ directory
cd desktop/
npm install  # First time only
npm run dev
```

### Alternative: Automated Startup (Experimental)
```bash
# From the desktop/ directory
cd desktop/
npm run dev
```

Note: The Rust code will attempt to start the Python backend automatically, but manual startup is more reliable.

### Manual Step-by-Step (for troubleshooting)

1. **Test Python backend separately**:
   ```bash
   # From project root
   python desktop_app.py
   ```
   - Should show dependency checks and start server on port 7860
   - Access http://127.0.0.1:7860 in browser to verify

2. **Start Tauri development mode**:
   ```bash
   # From desktop/ directory
   cd desktop/
   npx tauri dev
   ```

## 📦 Building for Production

### Debug Build (Faster, for testing)
```bash
cd desktop/
npx tauri build --debug
```

### Release Build (Optimized, for distribution)
```bash
cd desktop/
npx tauri build
```

### Build Outputs
Compiled applications will be in:
```
desktop/src-tauri/target/release/bundle/
├── deb/           # Linux .deb package
├── appimage/      # Linux AppImage
├── msi/           # Windows installer
└── dmg/           # macOS disk image
```

## 🔍 Troubleshooting

### Common Issues

**1. "FFmpeg not found"**
```bash
# Ubuntu/Debian
sudo apt-get install ffmpeg

# macOS  
brew install ffmpeg

# Windows
# Download from https://ffmpeg.org/download.html
# Add to PATH environment variable
```

**2. "Python packages missing"**
- The `desktop_app.py` should automatically install missing packages
- If it fails, manually run: `pip install -r requirements.txt`

**3. "Rust not found"**
```bash
# Install Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source ~/.cargo/env
```

**4. "Tauri configuration errors"**
```bash
# If you see errors like "Additional properties are not allowed"
# Ensure you're using compatible versions:

# Update npm dependencies
cd desktop/
npm install

# Check Tauri version
npx tauri --version
```

**5. "Backend not starting"**
```bash
# Test the Python backend separately
python desktop_app.py

# Check for port conflicts
lsof -i :7860  # Linux/macOS
netstat -an | findstr 7860  # Windows

# If port 7860 is busy, kill the process or change the port
```

**6. "Window shows blank/loading screen"**
- Ensure the Python backend started successfully
- Check http://127.0.0.1:7860 in a web browser first
- Look for CORS errors in the browser console (F12)
- Wait a few seconds for the server to fully initialize

**5. "Build fails on Linux"**
```bash
# Install additional dependencies for Linux builds
sudo apt-get install libwebkit2gtk-4.0-dev build-essential curl wget libssl-dev libgtk-3-dev libayatana-appindicator3-dev librsvg2-dev
```

**6. "CORS errors in console"**
- The FastAPI server includes CORS middleware for Tauri compatibility
- If you see CORS errors, ensure the server is running on exactly `127.0.0.1:7860`

### Debug Mode

Enable verbose logging:
```bash
# Set debug environment variables
export RUST_LOG=debug
export TAURI_DEBUG=true

# Run in debug mode
cd desktop/
npx tauri dev
```

## 📝 Development Notes

### File Structure
```
voice-separator-demucs/
├── desktop_app.py          # Desktop entry point (sidecar)
├── main.py                 # Web server entry point
├── src/                    # Shared Python codebase
├── templates/              # Shared Jinja2 templates  
├── static/                 # Shared static assets
└── desktop/                # Desktop-specific files
    ├── package.json        # Node.js dependencies
    ├── tauri.conf.json     # Tauri configuration
    └── src-tauri/          # Rust code
```

### Key Features
- ✅ **Shared codebase** - No code duplication between web and desktop
- ✅ **Auto dependency management** - Checks and installs requirements
- ✅ **System tray integration** - Minimize to tray instead of closing
- ✅ **Hot reload** - Changes reflected immediately during development
- ✅ **Cross-platform** - Windows, macOS, Linux support

### Performance Tips
- First run downloads Demucs models (~200MB) - this is normal
- Subsequent runs are much faster
- Desktop app uses the same AI models as the web version
- Processing times are identical to the web version

## 🌐 Switching Between Web and Desktop

You can run both versions simultaneously:

```bash
# Terminal 1: Web version (port 7860, 0.0.0.0)
python main.py

# Terminal 2: Desktop version (port 7860, 127.0.0.1)  
python desktop_app.py

# Terminal 3: Tauri development
cd desktop/
npx tauri dev
```

Note: They use the same port but different host bindings, so there's no conflict.

## 📞 Support

If you encounter issues:
1. Check this troubleshooting guide
2. Verify all prerequisites are installed
3. Test the Python backend separately with `python desktop_app.py`
4. Check the [main README.md](../README.md) for general application help
5. Open an issue on GitHub with detailed error messages

---

🎵 **Happy audio separating!** 🎤

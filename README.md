# Voice Separator - AI-Powered Audio Separation

A simple and efficient web application to separate audio elements (vocals, drums, bass, other instruments) from music using artificial intelligence.

## 🎵 What it does

![Voice Separator by @paladini - Main Page Interface](static/images/voice-separator-main-page.png)

- **Separate vocals** from background music (karaoke)
- **Extract instruments** individually (drums, bass, others)
- **Process YouTube videos** automatically
- **Easy web interface** - no programming required
- **Multiple formats** - supports MP3, WAV, FLAC, M4A, AAC

## 🚀 How to use

### Option 1: Docker (Recommended - Easiest)

If you have Docker installed:

```bash
# Download and run
docker compose up -d
```

Access [http://localhost:7860](http://localhost:7860).

**Done!** Skip to "Usage" below.

### Option 2: Python

**Prerequisites:**
- Python 3.8+
- FFmpeg installed

```bash
# 1. Install FFmpeg
sudo apt-get install ffmpeg  # Ubuntu/Debian
# or
brew install ffmpeg  # macOS

# 2. Navigate to project folder
cd voice-separator-demucs

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run
python main.py
```

Access [http://localhost:7860](http://localhost:7860).

## 🎵 Usage

### File Upload
1. **Select elements** (vocals, drums, bass, etc.)
2. **Choose audio file** (MP3, WAV, etc.)
3. **Click "Separate"**
4. **Wait** 2-5 minutes
5. **Download** results

### YouTube
1. **Select desired elements**
2. **Paste YouTube URL**
3. **Click "Download and Separate"**
4. **Wait** for download + processing
5. **Download** separated files

## ⚡ Quick tips

- **First time:** AI model will be downloaded (~200MB)
- **Vocals only:** Faster (~2 min)
- **All elements:** Slower (~5 min)
- **YouTube:** 10-minute video limit

## 📋 Supported formats

✅ **MP3**, WAV, FLAC, M4A, AAC  
📏 **Limit:** 100MB per file  
⏱️ **YouTube:** Maximum 10 minutes

## 🛠️ Technical details

This application uses **Demucs**, an AI model developed by Facebook/Meta AI specifically for music source separation. It's based on deep neural networks trained on thousands of songs.

### Architecture
- **Backend:** FastAPI + PyTorch + Demucs
- **Frontend:** Modern responsive web interface
- **AI Model:** MDX Extra Q (CPU-optimized)
- **Audio Processing:** FFmpeg + PyTorch Audio

### Performance
- **Optimized for CPU** (GPU optional)
- **Memory efficient** with dynamic model loading
- **Persistent model cache** to avoid re-downloads

## 🐳 Docker deployment

### Quick start
```bash
# Using docker-compose (recommended)
docker-compose up -d

# Or using Docker directly
docker build -t voice-separator .
docker run -p 7860:7860 -v $(pwd)/static/output:/app/static/output voice-separator
```

### Production deployment
```bash
# With persistent model cache
docker-compose -f docker-compose.yml up -d

# Models are cached in a Docker volume for better performance
```

## 🆘 Troubleshooting

**"FFmpeg not found"**
```bash
# Ubuntu/Debian
sudo apt-get install ffmpeg

# macOS
brew install ffmpeg

# Windows
# Download from https://ffmpeg.org/download.html
```

**Very slow processing**
- Use smaller files
- Close other programs
- Select fewer elements
- First run downloads AI model (~200MB)

**YouTube download error**
- Check if video is public
- Maximum 10 minutes duration
- Some videos may be region-locked

**Out of memory errors**
- Reduce file size
- Close other applications
- Use fewer simultaneous processes

## 🔧 Development

### Local setup
```bash
# Clone repository
git clone https://github.com/paladini/voice-separator-demucs.git
cd voice-separator-demucs

# Install dependencies
pip install -r requirements.txt

# Run development server
python main.py
```

### API documentation
- Interactive docs: `http://localhost:7860/docs`
- Alternative docs: `http://localhost:7860/redoc`

## 📝 Usage notes

This tool is intended for personal and educational use. Please respect the copyright of the music you process.

## 👨‍💻 Developed by

**Fernando Paladini** ([@paladini](https://github.com/paladini))

Based on the Demucs model by Facebook/Meta AI Research.

## 📄 License

This project is licensed under the MIT License. See the LICENSE file for details.

---

📖 **[Versão em Português](README_PT-BR.md)**

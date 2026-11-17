# Voice Separator - AI-Powered Audio Separation

[![License: MIT](https://img.shields.io/github/license/paladini/voice-separator-demucs)](LICENSE)
[![Docker Pulls](https://img.shields.io/docker/pulls/paladini/voice-separator)](https://hub.docker.com/r/paladini/voice-separator)
[![GHCR](https://img.shields.io/badge/ghcr.io-paladini%2Fvoice--separator-blue)](https://github.com/paladini/voice-separator-demucs/pkgs/container/voice-separator)
[![GitHub stars](https://img.shields.io/github/stars/paladini/voice-separator-demucs)](https://github.com/paladini/voice-separator-demucs/stargazers)

A simple and efficient self-hosted web application to separate audio elements (vocals, drums, bass, other instruments) from music using artificial intelligence.

## Docker images

- **CPU:** [`paladini/voice-separator:latest`](https://hub.docker.com/r/paladini/voice-separator)
- **NVIDIA GPU:** [`paladini/voice-separator:gpu`](https://hub.docker.com/r/paladini/voice-separator)

Both images are also available on [GHCR](https://github.com/paladini/voice-separator-demucs/pkgs/container/voice-separator).

## 🎵 What it does

![Voice Separator by @paladini - Main Page Interface](https://i.imgur.com/h1DY94R.png)

- **Separate vocals** from background music (karaoke)
- **Extract instruments** individually (drums, bass, others)
- **Process YouTube videos** automatically
- **Easy web interface** - no programming required
- **Multiple formats** - supports MP3, WAV, FLAC, M4A, AAC

## 🚀 How to use

### Option 1: Docker (Recommended - Easiest)

**Super simple - Just one command:**

```bash
# Method 1: Ultra-simple CPU (files saved inside container)
docker run -d -p 7860:7860 --name voice-separator paladini/voice-separator

# Method 2: Using docker-compose (files accessible on your computer)
git clone https://github.com/paladini/voice-separator-demucs.git
cd voice-separator-demucs
docker compose up -d
```

### NVIDIA GPU

The NVIDIA image uses CUDA-enabled PyTorch. It requires an NVIDIA GPU, a compatible driver, and the [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html).

```bash
# Run the published GPU image
docker run --gpus all -d -p 7860:7860 --name voice-separator paladini/voice-separator:gpu
```

To build from this repository with Docker Compose:

```bash
docker compose -f docker-compose.yml -f docker-compose.gpu.yml up -d --build
```

The GPU image uses the same web interface and port as the CPU image. Stop any existing Voice Separator container before starting the other variant.

Access [http://localhost:7860](http://localhost:7860).

**Done!** If using Method 2, your files will appear in the `static/output/` folder.

## 📥 Getting your files

**If you used Method 1 (ultra-simple):**
```bash
# Copy files from container to your computer
docker cp voice-separator:/app/static/output ./my-separated-files/
```

**If you used Method 2:**
- Files are already in your `static/output/` folder!

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

---

## 🔒 Local HTTPS & Browser Security Warnings

By default, the app runs on plain HTTP for simplicity. Modern browsers may show warnings like "Not Secure" or block downloads when using HTTP, even for local apps. This is normal and safe for local use.

**To avoid these warnings:**

1. **Use HTTPS locally with a self-signed certificate:**
   - Generate a certificate (one-time):
     ```bash
     openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes -subj "/CN=localhost"
     ```
   - Run the app with HTTPS:
     ```bash
     uvicorn main:app --host 0.0.0.0 --port 7860 --reload --ssl-keyfile=key.pem --ssl-certfile=cert.pem
     ```
   - Access the app at [https://localhost:7860](https://localhost:7860) and accept the browser warning about the self-signed certificate.

2. **You may commit and reuse the same `.pem` files for local development.**
   - This is safe for local-only use. Never use these files in production.
   - All users will see a browser warning the first time, unless they add the certificate to their trusted store (not required for local dev).

3. **If you use plain HTTP:**
   - You may see "Not Secure" warnings and Chrome may block downloads. You can safely click "Keep" or "Download anyway" for your own files.

**Summary:**
- For local use, these warnings are not a risk.
- For the best user experience, use HTTPS as above.
- Always access the app at [http://localhost:7860](http://localhost:7860) or [https://localhost:7860](https://localhost:7860), not `0.0.0.0`.

Access [http://localhost:7860](http://localhost:7860).

## 🎵 Usage
### Model Selection Feature

You can now choose between different AI models for separation:

- **Demucs CPU Lite (mdx_extra_q):** Fastest, runs on any CPU (default).
- **Demucs v3 (mdx):** Fast, GPU recommended for best speed.
- **Demucs v4 (htdemucs):** Medium speed, GPU required.
- **Demucs HD (htdemucs_ft):** Best quality, GPU required.

**How to use:**
- By default, the fastest model (Demucs CPU Lite) is used for all separations.
- To select a different model, enable the "Model selection" toggle in the web interface. This will reveal a dropdown where you can choose your preferred model.
- If the toggle is not enabled, the model selection UI is hidden and the default model is used.

**Tip:** If you do not have a GPU, select Demucs CPU Lite for best compatibility and speed.

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
📏 **Limit:** No file size limit (local use)
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

### Ultra-simple deployment

**Option A: Direct from Docker Hub (no code download needed)**
```bash
# Ultra-simple (files stay in container)
docker run -d -p 7860:7860 --name voice-separator paladini/voice-separator

# Recommended (files accessible on host)
mkdir -p voice-separator-output
docker run -d -p 7860:7860 -v $(pwd)/voice-separator-output:/app/static/output --name voice-separator paladini/voice-separator

# Access: http://localhost:7860
# Files saved to: ./voice-separator-output/ (if using second command)
```

**Option B: Using docker-compose (with source code)**
```bash
# Clone and run
git clone https://github.com/paladini/voice-separator-demucs.git
cd voice-separator-demucs
docker compose up -d

# Access: http://localhost:7860
# Files saved to: ./static/output/
```

**Option C: NVIDIA GPU**

The `latest` image is CPU-only. Use the `gpu` image for NVIDIA acceleration. Both variants expose the same web interface and use port 7860.

Build locally with `Dockerfile.gpu` (CUDA 12.6 PyTorch on `nvidia/cuda`). Needs the [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html):

```bash
# Intended GPU Compose path: overlay (one service on 7860)
docker compose -f docker-compose.yml -f docker-compose.gpu.yml up -d --build

# Same image after a local build
docker build -f Dockerfile.gpu -t paladini/voice-separator:gpu .
docker run --gpus all -d -p 7860:7860 \
  -v $(pwd)/voice-separator-output:/app/static/output \
  --name voice-separator \
  paladini/voice-separator:gpu
```

`docker compose --profile gpu up -d` may start **both** the default CPU service and `voice-separator-gpu`, both bound to **7860**. Prefer the overlay file. If you use the profile, name the GPU service and stop the CPU container first: `docker compose --profile gpu up -d voice-separator-gpu`.

The GPU image is also available from GHCR as `ghcr.io/paladini/voice-separator:gpu`. Hub listing text: [`docs/docker-hub-overview.md`](docs/docker-hub-overview.md).

### NAS / homelab templates

- Unraid Community Apps–style XML: [`deploy/unraid/voice-separator.xml`](deploy/unraid/voice-separator.xml) (CPU) and [`voice-separator-gpu.xml`](deploy/unraid/voice-separator-gpu.xml)
- TrueNAS SCALE compose: [`deploy/truenas/docker-compose.yml`](deploy/truenas/docker-compose.yml)

### Management commands
```bash
# Stop container
docker stop voice-separator

# Start again
docker start voice-separator

# Remove container
docker rm voice-separator

# Update the CPU image
docker pull paladini/voice-separator:latest
# Pull the NVIDIA GPU image
docker pull paladini/voice-separator:gpu
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

### Verify mono/stereo behavior (manual)
After starting the app (`python main.py`), you can create short test files and run both separation paths:

```bash
# 1) Create 5-second 48 kHz mono and stereo test tones
ffmpeg -f lavfi -i "sine=frequency=440:sample_rate=48000:duration=5" -ac 1 -ar 48000 ./test-mono.wav -y
ffmpeg -f lavfi -i "sine=frequency=440:sample_rate=48000:duration=5" -ac 2 -ar 48000 ./test-stereo.wav -y

# 2) Submit mono file
curl -X POST "http://localhost:7860/api/separate" \
  -F "file=@./test-mono.wav" \
  -F "stems=vocals"

# 3) Submit stereo file
curl -X POST "http://localhost:7860/api/separate" \
  -F "file=@./test-stereo.wav" \
  -F "stems=vocals"
```

Both requests should return `success: true` and generated MP3 paths.

### Run unit tests for channel normalization
```bash
python -m unittest tests/test_audio_tensor_utils.py -v
```

## 📝 Usage notes

This tool is intended for personal and educational use. Please respect the copyright of the music you process.

## 👨‍💻 Developed by

**Fernando Paladini** ([@paladini](https://github.com/paladini))

Based on the Demucs model by Facebook/Meta AI Research.

## 📄 License

This project is licensed under the MIT License. See the LICENSE file for details.

---

📖 **[Versão em Português do Brasil](README_PT-BR.md)**

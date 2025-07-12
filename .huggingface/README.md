---
title: Voice Separator - AI-Powered Audio Separation
emoji: 🎤
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
pinned: false
license: mit
short_description: Separate vocals and instruments from audio using AI-powered Demucs model
tags:
- audio
- music
- demucs
- source-separation
- vocals
- karaoke
- fastapi
- pytorch
- ai
- machine-learning
models:
- facebook/demucs
datasets: []
app_file: main.py
python_version: "3.9"
---

<!-- This header is only visible on Hugging Face Spaces, not on GitHub -->

# Voice Separator - AI-Powered Audio Separation

🎵 **Live Demo:** Try it now on [Hugging Face Spaces](https://huggingface.co/spaces/paladini/voice-separator)

A simple and efficient web application to separate audio elements (vocals, drums, bass, other instruments) from music using the Demucs AI model by Meta AI.

## Quick Start

1. Upload an audio file or paste a YouTube URL
2. Select which elements to extract (vocals, drums, bass, etc.)
3. Wait 2-5 minutes for AI processing
4. Download your separated audio files

## Features

- 🎵 **Vocal isolation** - Perfect for karaoke
- 🥁 **Instrument separation** - Extract drums, bass, others individually  
- 📺 **YouTube support** - Process videos directly from URLs
- 🚀 **Fast processing** - Optimized AI model for quick results
- 💻 **No installation** - Works directly in your browser

---

*For installation instructions and technical details, visit the [GitHub repository](https://github.com/paladini/voice-separator-demucs)*
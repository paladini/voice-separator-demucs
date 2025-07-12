# Voice Separator - Desktop Version

This directory contains the Tauri-based desktop application for Voice Separator.

## Quick Start

```bash
# From this directory
npm install
npx tauri dev
```

## Architecture

- **Frontend**: Web UI loaded from local FastAPI server (http://127.0.0.1:7860)
- **Backend**: Python FastAPI server running as Tauri sidecar
- **No build step**: Direct "Live Server" approach for unified development

## Files

- `package.json`: Node.js dependencies for Tauri CLI
- `tauri.conf.json`: Tauri configuration (window settings, sidecar, permissions)
- `src-tauri/`: Rust code for the desktop application
- `src-tauri/icons/`: Application icons (you need to add these)

## Icon Requirements

You need to add icons in the following formats to `src-tauri/icons/`:
- `32x32.png`
- `128x128.png` 
- `128x128@2x.png`
- `icon.icns` (macOS)
- `icon.ico` (Windows)
- `icon.png` (Linux)

## See Also

- [DESKTOP_QUICKSTART.md](../DESKTOP_QUICKSTART.md) - Complete setup guide
- [../README.md](../README.md) - Main application documentation

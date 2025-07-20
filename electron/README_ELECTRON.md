# Voice Separator Desktop (Electron)

## How to Run (Development)

1. **Install Node.js (LTS) and Python 3.8+**
2. `cd electron`
3. `npm install`
4. (Optional) Set `PYTHON_PATH` if not `python3` on your system
5. `npm start`

- The Electron app will launch and manage the FastAPI backend automatically.
- All processing is local. No internet required after install (except for model download).

## Packaging

- Use `electron-builder` or `electron-forge` for cross-platform builds:
  - `npm run build` (see package.json for scripts)

## Features
- Modern, minimal UI
- Hardware detection (CPU, RAM, GPU)
- Model selection (with toggle)
- Native file dialogs for open/save
- Output folder access
- Cross-platform: Ubuntu, Windows 10/11, macOS

## Security & Performance
- Backend runs only when app is open
- No remote code execution
- Minimal RAM/CPU usage

## Troubleshooting
- If backend fails to start, check Python path and dependencies
- GPU detection may vary by OS; fallback to CPU if not detected

---

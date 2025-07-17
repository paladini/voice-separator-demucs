# Copilot Instructions for Voice Separator Demucs

## Project Overview
- **Voice Separator** is a FastAPI web app for AI-powered music source separation using Meta AI's Demucs model.
- Main features: upload audio files or YouTube URLs, select stems (vocals, drums, bass, other), and download separated tracks.
- Architecture: Python backend (`src/core` for logic, `src/api` for REST API), modern HTML/CSS/JS frontend (`templates/index.html`, `static/css/style.css`).

## Key Directories & Files
- `src/core/separator.py`: Demucs integration, stem definitions, audio separation logic.
- `src/core/youtube_downloader.py`: YouTube audio download and preprocessing.
- `src/api/routes.py`: FastAPI endpoints (`/api/separate`, `/api/separate-youtube`, `/api/stems`), file validation, request handling.
- `main.py`: App entry point; runs FastAPI server.
- `templates/index.html`: Main UI, stem selection, upload/YouTube forms, results display.
- `static/output/`: Separated audio files (MP3).

## Developer Workflows
- **Run locally:**
  - `python main.py` (or `uvicorn main:app --host 0.0.0.0 --port 7860 --reload`)
  - Access UI at [http://localhost:7860](http://localhost:7860)
- **Docker:**
  - `docker compose up -d` (recommended; files in `static/output/`)
  - For container-only: `docker run -d -p 7860:7860 --name voice-separator paladini/voice-separator`
- **Install dependencies:** `pip install -r requirements.txt`
- **FFmpeg required:** Must be installed on host (see README for install commands).

## API & Data Flow
- User selects stems and uploads file or YouTube URL via frontend.
- Frontend JS validates file type/size (max 100MB, MP3/WAV/FLAC/M4A/AAC) and YouTube URL (max 10 min, public).
- `/api/separate` (file) and `/api/separate-youtube` (YouTube) endpoints process requests, call separation logic, and return download links for each stem.
- Results are displayed dynamically; download links use stem icons/names from backend config.

## Patterns & Conventions
- **Stem system:** Stems defined in `AVAILABLE_STEMS` (icon, name, index) in `separator.py` and reflected in UI.
- **Error handling:** Frontend displays user-friendly messages and suggestions based on error type (see JS in `index.html`).
- **Processing warnings:** UI warns if multiple stems selected (slower processing).
- **Model caching:** First run downloads Demucs model (~200MB); subsequent runs use cached model.
- **Output files:** Always saved as MP3 in `static/output/` (or container volume).

## Integration Points
- **Demucs**: Used via Python API, not CLI. Model selection and stem mapping handled in backend.
- **YouTube**: Downloaded audio is preprocessed before separation.
- **FFmpeg**: Used for audio conversion; must be present on host/container.

## Troubleshooting
- Common issues: missing FFmpeg, large files, unsupported formats, YouTube restrictions, out-of-memory errors.
- See `README.md` and `README_PT-BR.md` for solutions and tips.

## Examples
- To add a new stem, update `AVAILABLE_STEMS` in `separator.py` and reflect changes in frontend UI.
- To change output format, modify audio export logic in `separator.py` and update frontend download handling.

---
**For more details, see:**
- `README.md` (English)
- `README_PT-BR.md` (Português)
- `src/core/separator.py`, `src/api/routes.py`, `templates/index.html`

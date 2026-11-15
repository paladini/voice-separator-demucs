# Docker Hub listing (paste into paladini/voice-separator)

**Short description (Hub “Description” field):**

Self-hosted Demucs web UI to separate vocals, drums, bass, and other stems. CPU default; optional NVIDIA `:gpu` tag.

**Full description (Hub “Full description” / README):**

# Voice Separator

Web UI for [Demucs](https://github.com/facebookresearch/demucs) music source separation. Upload a file or a YouTube URL, pick stems, download MP3s.

- **GitHub:** https://github.com/paladini/voice-separator-demucs
- **GHCR:** `ghcr.io/paladini/voice-separator` (same tags as Hub)

## Tags

| Tag | What it is | Command |
| --- | --- | --- |
| `latest` (default) | CPU image. This is `docker run paladini/voice-separator`. | `docker run -d -p 7860:7860 --name voice-separator paladini/voice-separator` |
| `gpu` | NVIDIA CUDA 12.6 + CUDA PyTorch. Needs NVIDIA Container Toolkit. | `docker run --gpus all -d -p 7860:7860 --name voice-separator paladini/voice-separator:gpu` |

Do **not** pass `--gpus` to `:latest`. That image does not include CUDA PyTorch, so CUDA will not work.

Web UI: **http://localhost:7860** (not 8000).

## CPU (recommended default)

```bash
docker run -d -p 7860:7860 \
  -v "$PWD/voice-separator-output:/app/static/output" \
  --name voice-separator \
  paladini/voice-separator
```

Compose (from the Git repo): `docker compose up -d`

## NVIDIA GPU

Requirements: NVIDIA driver + [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html).

```bash
docker run --gpus all -d -p 7860:7860 \
  -v "$PWD/voice-separator-output:/app/static/output" \
  --name voice-separator \
  paladini/voice-separator:gpu
```

Compose overlay:

```bash
docker compose -f docker-compose.yml -f docker-compose.gpu.yml up -d
# or
docker compose --profile gpu up -d voice-separator-gpu
```

Verify CUDA inside the GPU container:

```bash
docker exec voice-separator python -c "import torch; print(torch.cuda.is_available(), torch.version.cuda)"
```

Expect `True` and a CUDA version. If this prints `False`, the GPU image cannot accelerate Demucs on that host.

## Persistence

| Path | Purpose |
| --- | --- |
| `/app/static/output` | Separated MP3s |
| `/root/.cache` | Demucs / torch hub cache (first run downloads models) |

## Unraid / TrueNAS

Templates live in the Git repo: `deploy/unraid/` and `deploy/truenas/`.

## License

MIT. Personal/educational use; respect copyright of the audio you process.

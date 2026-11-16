# Docker Hub listing (paste into paladini/voice-separator)

Paste the short description now. Paste the GPU Hub command **only after** you push a `gpu` tag to this Hub repo — that tag is **not** published yet. Until then, GPU is local `Dockerfile.gpu` / GHCR after the publish workflow.

**Short description (Hub “Description” field):**

Self-hosted Demucs web UI to separate vocals, drums, bass, and other stems. CPU default (`docker run -p 7860 paladini/voice-separator`). NVIDIA GPU is a separate image (build locally / GHCR; Hub `:gpu` after it is pushed).

**Full description (Hub “Full description” / README):**

# Voice Separator

Web UI for [Demucs](https://github.com/facebookresearch/demucs) music source separation. Upload a file or a YouTube URL, pick stems, download MP3s.

- **GitHub:** https://github.com/paladini/voice-separator-demucs
- **GHCR:** `ghcr.io/paladini/voice-separator` (CPU `latest` today; `:gpu` only after the GHCR workflow with `variant=gpu`)

## Tags

| Tag | What it is | Status |
| --- | --- | --- |
| `latest` (default) | CPU image. This is `docker run paladini/voice-separator`. | **On Hub now.** |
| `gpu` | NVIDIA CUDA 12.6 + CUDA PyTorch. Needs NVIDIA Container Toolkit. | **Not on Hub yet.** Build locally, or pull GHCR after the gpu workflow, or Hub after the maintainer pushes `:gpu`. |

Do **not** pass `--gpus` to `:latest`. That image does not include CUDA PyTorch, so CUDA will not work. Do not run `docker run … paladini/voice-separator:gpu` against Hub until that tag exists.

Web UI: **http://localhost:7860** (not 8000).

## CPU (recommended default — this is what Hub serves today)

```bash
docker run -d -p 7860:7860 \
  -v "$PWD/voice-separator-output:/app/static/output" \
  --name voice-separator \
  paladini/voice-separator
```

Compose (from the Git repo): `docker compose up -d`

## NVIDIA GPU

Requirements: NVIDIA driver + [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html). Hub has no `gpu` tag until it is pushed.

**1. Build locally** (works today):

```bash
git clone https://github.com/paladini/voice-separator-demucs.git
cd voice-separator-demucs
docker build -f Dockerfile.gpu -t paladini/voice-separator:gpu .
docker run --gpus all -d -p 7860:7860 \
  -v "$PWD/voice-separator-output:/app/static/output" \
  --name voice-separator \
  paladini/voice-separator:gpu
```

**Intended Compose path** (overlay — one service on 7860):

```bash
docker compose -f docker-compose.yml -f docker-compose.gpu.yml up -d --build
```

Do **not** run `docker compose --profile gpu up -d` without a service name: the CPU service has no profile, so Compose may start **both** CPU and GPU on port **7860**. If you use the profile, name the GPU service and stop the CPU container first: `docker compose --profile gpu up -d voice-separator-gpu`.

**2. GHCR after the workflow:** `ghcr.io/paladini/voice-separator:gpu` (Publish to GHCR, `variant=gpu`, `source_tag=gpu`, mode `build` until Hub has `:gpu` to mirror).

**3. After you push `:gpu` to Hub**, this works (not before):

```bash
docker run --gpus all -d -p 7860:7860 \
  -v "$PWD/voice-separator-output:/app/static/output" \
  --name voice-separator \
  paladini/voice-separator:gpu
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

Templates live in the Git repo: `deploy/unraid/` and `deploy/truenas/`. The Unraid GPU template’s Hub repository name works only after `:gpu` is on Hub; until then build locally or use GHCR after the workflow.

## License

MIT. Personal/educational use; respect copyright of the audio you process.

# awesome-selfhosted submission (owner action)

Listings are **not** edited on [awesome-selfhosted/awesome-selfhosted](https://github.com/awesome-selfhosted/awesome-selfhosted). Add YAML under [awesome-selfhosted/awesome-selfhosted-data](https://github.com/awesome-selfhosted/awesome-selfhosted-data).

Their [CONTRIBUTING.md](https://github.com/awesome-selfhosted/awesome-selfhosted-data/blob/master/CONTRIBUTING.md) **forbids machine/LLM-generated pull requests**. Do not open this PR from an automated agent account.

## Checklist (from their PR template)

- One item per PR
- Human submission
- Search closed/open issues and PRs for “Voice Separator” / paladini (none as of 2026-11-15)
- Not listed on awesome-sysadmin / staticgen / dbdb.io
- Actively maintained
- First release older than 4 months (Hub tags `1.0` / `1.1` from 2025; repo activity through 2026)
- Working install docs (`docker run -p 7860 …`)
- kebab-case filename `software/voice-separator.yml`
- No unused optional fields / comments in the file that lands on their repo
- Platforms: `Python`, `Docker`
- First tag is the single-page category: **Media Streaming - Multimedia Streaming** (Audio/Multimedia family; Karaoke Eternal uses this tag). Second: **Media Management**.

## Exact PR to open

1. Fork https://github.com/awesome-selfhosted/awesome-selfhosted-data
2. Add **`software/voice-separator.yml`** with the contents of [`voice-separator.yml`](./voice-separator.yml) **minus the comment header**.
3. Commit message: `add Voice Separator`
4. PR title: **`Add Voice Separator to Media Streaming - Multimedia Streaming`**
5. PR body: tick their template boxes; link https://github.com/paladini/voice-separator-demucs and https://hub.docker.com/r/paladini/voice-separator
6. Target repo: `awesome-selfhosted/awesome-selfhosted-data` (master). The markdown list is generated from this data repo.

Rendered markdown form (legacy README style, for reference only):

```markdown
- [Voice Separator](https://github.com/paladini/voice-separator-demucs) - Web UI for Demucs music source separation. Split vocals, drums, bass, and other stems from uploads or YouTube URLs. `MIT` `Python/Docker`
```

## Optional Hub paste

After merging the GPU/docs PR, paste [`docs/docker-hub-overview.md`](../docker-hub-overview.md) into the Docker Hub repository description so Hub matches port 7860 and the `gpu` tag.

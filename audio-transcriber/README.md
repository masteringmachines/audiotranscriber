# Lingua — Offline Audio-to-Subtitle Translator

Upload any audio file, get a translated `.srt` subtitle file in **Spanish** or **Mandarin** — fully offline, no API keys, no audio sent to any external service.

## How it works

```
Audio file
    ↓  faster-whisper (local Whisper model, CPU)
English transcript (timed segments)
    ↓  Argos Translate (offline OpenNMT models)
Spanish / Mandarin translation
    ↓  SRT formatter
output.srt
```

## Quick start

```bash
pip install -e ".[dev]"

# Web UI (recommended)
lingua-web
# → open http://localhost:5000

# CLI (batch / scripting)
lingua-cli audio/interview.mp3 --lang es --output interview_spanish.srt
lingua-cli audio/podcast.m4a   --lang zh --model small
```

## Project layout

```
audio-transcriber/
├── src/audio_transcriber/
│   ├── transcriber.py   # faster-whisper wrapper → List[Segment]
│   ├── translator.py    # Argos Translate wrapper, auto-downloads packages
│   ├── srt.py           # SRT formatter + timestamp converter
│   ├── pipeline.py      # transcribe → translate → SRT (single entry point)
│   ├── app.py           # Flask web app
│   ├── server.py        # `lingua-web` entry point
│   └── cli.py           # `lingua-cli` entry point
├── templates/
│   └── index.html       # Single-page upload UI
└── tests/
    ├── test_srt.py          # SRT formatting (no deps)
    └── test_pipeline_unit.py # Mocked pipeline + Flask route tests
```

## Supported audio formats

mp3, wav, m4a, ogg, flac, webm — anything ffmpeg can read.

## Model sizes

| Model  | Size   | Speed (CPU) | Accuracy |
|--------|--------|-------------|----------|
| tiny   | 75 MB  | ~5x realtime | Good    |
| base   | 140 MB | ~3x realtime | Better  |
| small  | 460 MB | ~1x realtime | Great   |
| medium | 1.5 GB | ~0.5x realtime | Best  |

**First run:** Whisper models download to `~/.cache/huggingface`. Argos language packages download to `~/.local/share/argos-translate/packages`. Both are cached permanently — subsequent runs start instantly.

## Tests

```bash
pytest -q
```

Tests mock all heavy deps (Whisper, Argos) so they run offline with just `flask` and `pytest` installed.

## Dependencies

- [faster-whisper](https://github.com/SYSTRAN/faster-whisper) — CTranslate2-based Whisper, no PyTorch
- [argostranslate](https://github.com/argosopentech/argos-translate) — offline neural translation
- [Flask](https://flask.palletsprojects.com/) — web server

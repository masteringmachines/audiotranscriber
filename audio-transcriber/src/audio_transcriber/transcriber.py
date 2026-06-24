"""Transcription via faster-whisper (CPU-friendly Whisper reimplementation).

faster-whisper uses CTranslate2 — same accuracy as OpenAI Whisper but ~4x
faster on CPU with no PyTorch required. The model (~140 MB for "base") is
downloaded once to ~/.cache/huggingface on first run, then reused from disk.
"""
from dataclasses import dataclass
from pathlib import Path
from typing import List


@dataclass
class Segment:
    start: float   # seconds
    end: float
    text: str


def transcribe(audio_path: str, model_size: str = "base") -> List[Segment]:
    """Transcribe audio and return timed text segments.

    Supports any format ffmpeg understands: mp3, wav, m4a, ogg, flac, webm.
    model_size: "tiny" (75 MB) | "base" (140 MB) | "small" (460 MB) | "medium" (1.5 GB)
    """
    try:
        from faster_whisper import WhisperModel
    except ImportError as exc:
        raise RuntimeError(
            "faster-whisper not installed — run: pip install faster-whisper"
        ) from exc

    if not Path(audio_path).exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    model = WhisperModel(model_size, device="cpu", compute_type="int8")
    raw_segments, _ = model.transcribe(audio_path, beam_size=5)

    return [
        Segment(start=s.start, end=s.end, text=s.text.strip())
        for s in raw_segments
        if s.text.strip()
    ]

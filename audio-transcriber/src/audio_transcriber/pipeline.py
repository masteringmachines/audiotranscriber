"""Top-level pipeline: audio file → translated SRT string.

This is the single entry point used by both the web UI and any future CLI.
It chains transcribe() → translate_segments() → segments_to_srt() and
returns the SRT content as a string so the caller decides what to do with it
(stream it to a browser, write it to disk, etc.).
"""
from .srt import segments_to_srt
from .transcriber import transcribe
from .translator import translate_segments


def run(
    audio_path: str,
    target_lang: str = "es",
    model_size: str = "base",
) -> str:
    """Transcribe *audio_path* and return an SRT string translated to *target_lang*.

    Args:
        audio_path:  Path to any audio file ffmpeg can read.
        target_lang: "es" (Spanish) or "zh" (Mandarin).
        model_size:  Whisper model size — "tiny", "base", "small", "medium".

    Returns:
        SRT-formatted string ready to write to a .srt file.
    """
    segments = transcribe(audio_path, model_size=model_size)
    translated = translate_segments(segments, target_lang=target_lang)
    return segments_to_srt(translated)

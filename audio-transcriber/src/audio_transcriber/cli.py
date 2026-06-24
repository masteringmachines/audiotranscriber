"""Minimal CLI — for scripting and batch use without the web UI."""
import argparse
import sys
from pathlib import Path

from .pipeline import run
from .translator import SUPPORTED


def main(argv=None):
    p = argparse.ArgumentParser(
        description="Transcribe audio and output a translated SRT subtitle file."
    )
    p.add_argument("audio", help="Audio file path (mp3, wav, m4a, ogg, flac, webm)")
    p.add_argument(
        "--lang", choices=list(SUPPORTED), default="es",
        help="Target language: es=Spanish, zh=Mandarin (default: es)"
    )
    p.add_argument(
        "--model", choices=["tiny", "base", "small", "medium"], default="base",
        help="Whisper model size (default: base)"
    )
    p.add_argument("--output", "-o", help="Output .srt path (default: <audio_stem>_<lang>.srt)")
    args = p.parse_args(argv)

    out = args.output or f"{Path(args.audio).stem}_{args.lang}.srt"
    print(f"Transcribing {args.audio} → {out} ({SUPPORTED[args.lang]}) ...")

    try:
        srt = run(args.audio, target_lang=args.lang, model_size=args.model)
    except Exception as exc:
        sys.exit(f"Error: {exc}")

    Path(out).write_text(srt, encoding="utf-8")
    print(f"Done. SRT saved to: {out}")


if __name__ == "__main__":
    main()

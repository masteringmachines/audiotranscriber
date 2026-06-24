"""Translation via Argos Translate — fully offline, no API keys.

Argos uses pre-trained OpenNMT models. Language packages are downloaded once
and stored in ~/.local/share/argos-translate/packages (Linux) or the OS
equivalent, then reused from disk on every subsequent run.

Supported target languages: "es" (Spanish), "zh" (Mandarin).
Source language is always "en" (English) — Whisper transcribes to English
by default regardless of the original audio language.
"""
from typing import List

from .transcriber import Segment

SUPPORTED: dict[str, str] = {
    "es": "Spanish",
    "zh": "Mandarin",
}


def _ensure_package(source: str, target: str) -> None:
    """Download the Argos language package if not already installed."""
    try:
        import argostranslate.package as pkg
        import argostranslate.translate as tr
    except ImportError as exc:
        raise RuntimeError(
            "argostranslate not installed — run: pip install argostranslate"
        ) from exc

    available = {(p.from_code, p.to_code) for p in tr.get_installed_languages()
                 if hasattr(p, "from_code")}

    # Build the set from installed packages properly
    installed_pairs = set()
    for lang in tr.get_installed_languages():
        for translation in lang.translations_from:
            installed_pairs.add((lang.code, translation.to_lang.code))

    if (source, target) not in installed_pairs:
        pkg.update_package_index()
        available_pkgs = pkg.get_available_packages()
        package = next(
            (p for p in available_pkgs
             if p.from_code == source and p.to_code == target),
            None,
        )
        if package is None:
            raise RuntimeError(
                f"No Argos package found for {source} → {target}. "
                "Check https://www.argosopentech.com for supported pairs."
            )
        pkg.install_from_path(package.download())


def translate_segments(
    segments: List[Segment], target_lang: str
) -> List[Segment]:
    """Return a new list of Segments with text translated to *target_lang*.

    The timestamps from the original transcription are preserved so the SRT
    output stays in sync with the audio.
    """
    if target_lang not in SUPPORTED:
        raise ValueError(
            f"Unsupported language '{target_lang}'. "
            f"Choose from: {list(SUPPORTED)}"
        )

    try:
        import argostranslate.translate as tr
    except ImportError as exc:
        raise RuntimeError(
            "argostranslate not installed — run: pip install argostranslate"
        ) from exc

    _ensure_package("en", target_lang)

    # Resolve the en → target translation object
    en_lang = next(
        (l for l in tr.get_installed_languages() if l.code == "en"), None
    )
    if en_lang is None:
        raise RuntimeError("English source language not found in Argos packages.")

    target_lang_obj = next(
        (t.to_lang for t in en_lang.translations_from if t.to_lang.code == target_lang),
        None,
    )
    if target_lang_obj is None:
        raise RuntimeError(
            f"Translation en→{target_lang} not available after package install."
        )

    translation = en_lang.get_translation(target_lang_obj)

    return [
        Segment(
            start=seg.start,
            end=seg.end,
            text=translation.translate(seg.text),
        )
        for seg in segments
    ]

"""SRT subtitle file writer.

SRT format:
    1
    00:00:01,000 --> 00:00:04,500
    Text of the subtitle.

    2
    ...
"""
from typing import List
from .transcriber import Segment


def _fmt_time(seconds: float) -> str:
    """Convert float seconds to SRT timestamp HH:MM:SS,mmm."""
    ms = int(round(seconds * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1_000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def segments_to_srt(segments: List[Segment]) -> str:
    """Return an SRT-formatted string for *segments*."""
    blocks = []
    for i, seg in enumerate(segments, start=1):
        blocks.append(
            f"{i}\n"
            f"{_fmt_time(seg.start)} --> {_fmt_time(seg.end)}\n"
            f"{seg.text}\n"
        )
    return "\n".join(blocks)


def write_srt(segments: List[Segment], path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write(segments_to_srt(segments))

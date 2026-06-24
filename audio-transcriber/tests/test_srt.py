"""Tests for SRT formatting — no audio or model dependencies needed."""
from audio_transcriber.srt import _fmt_time, segments_to_srt
from audio_transcriber.transcriber import Segment


def test_fmt_time_basic():
    assert _fmt_time(0.0)      == "00:00:00,000"
    assert _fmt_time(1.5)      == "00:00:01,500"
    assert _fmt_time(61.0)     == "00:01:01,000"
    assert _fmt_time(3661.0)   == "01:01:01,000"
    assert _fmt_time(3723.456) == "01:02:03,456"


def test_fmt_time_millisecond_rounding():
    assert _fmt_time(0.7777) == "00:00:00,778"   # 777.7ms → 778
    assert _fmt_time(1.9999) == "00:00:02,000"   # 1999.9ms → 2000


def test_segments_to_srt_structure():
    segs = [
        Segment(start=0.0, end=2.5,  text="Hola mundo"),
        Segment(start=3.0, end=5.0,  text="¿Cómo estás?"),
    ]
    srt = segments_to_srt(segs)
    lines = srt.strip().split("\n")

    assert lines[0] == "1"
    assert "00:00:00,000 --> 00:00:02,500" in lines[1]
    assert lines[2] == "Hola mundo"
    assert lines[4] == "2"
    assert lines[6] == "¿Cómo estás?"


def test_segments_to_srt_empty():
    assert segments_to_srt([]) == ""


def test_srt_index_is_sequential():
    segs = [Segment(start=i, end=i+1, text=f"Line {i}") for i in range(5)]
    srt = segments_to_srt(segs)
    blocks = [b.strip() for b in srt.split("\n\n") if b.strip()]
    for idx, block in enumerate(blocks, start=1):
        assert block.startswith(str(idx))

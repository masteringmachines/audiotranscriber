"""Unit tests that mock the heavy deps (Whisper, Argos) so they run offline."""
from unittest.mock import MagicMock, patch

from audio_transcriber.transcriber import Segment


def _make_segments():
    return [
        Segment(start=0.0, end=2.0, text="Hello world"),
        Segment(start=2.5, end=4.0, text="How are you"),
    ]


def test_pipeline_chains_correctly():
    """pipeline.run() should call transcribe → translate → srt in order."""
    fake_translated = [
        Segment(start=0.0, end=2.0, text="Hola mundo"),
        Segment(start=2.5, end=4.0, text="Cómo estás"),
    ]
    with patch("audio_transcriber.pipeline.transcribe", return_value=_make_segments()) as mock_t, \
         patch("audio_transcriber.pipeline.translate_segments", return_value=fake_translated) as mock_tr, \
         patch("audio_transcriber.pipeline.segments_to_srt", return_value="SRT_OUTPUT") as mock_srt:

        from audio_transcriber.pipeline import run
        result = run("/fake/audio.mp3", target_lang="es", model_size="tiny")

        mock_t.assert_called_once_with("/fake/audio.mp3", model_size="tiny")
        mock_tr.assert_called_once_with(_make_segments(), target_lang="es")
        mock_srt.assert_called_once_with(fake_translated)
        assert result == "SRT_OUTPUT"


def test_translate_rejects_unknown_language():
    from audio_transcriber.translator import translate_segments
    with patch("audio_transcriber.translator._ensure_package"):
        try:
            translate_segments(_make_segments(), target_lang="fr")
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "fr" in str(e)


def test_flask_index_returns_200():
    with patch("audio_transcriber.app.render_template", return_value="<html>ok</html>"):
        from audio_transcriber.app import app
        app.config["TESTING"] = True
        client = app.test_client()
        res = client.get("/")
        assert res.status_code == 200


def test_flask_transcribe_no_file_returns_400():
    from audio_transcriber.app import app
    app.config["TESTING"] = True
    client = app.test_client()
    res = client.post("/transcribe", data={})
    assert res.status_code == 400


def test_flask_transcribe_bad_extension_returns_400():
    from audio_transcriber.app import app
    import io
    app.config["TESTING"] = True
    client = app.test_client()
    data = {"audio": (io.BytesIO(b"fake"), "file.exe"), "language": "es"}
    res = client.post("/transcribe", data=data, content_type="multipart/form-data")
    assert res.status_code == 400

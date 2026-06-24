"""Flask web application — upload audio, pick language, download SRT.

Intentionally thin: no database, no auth, no job queue. Files live in a
temporary directory for the duration of each request and are deleted
immediately after the response is sent. This keeps the server stateless
and avoids accumulating user audio on disk.

For production use with large files or slow CPUs, replace the synchronous
pipeline.run() call with a Celery task and poll for completion.
"""
import os
import tempfile
from pathlib import Path

from flask import Flask, Response, render_template, request, stream_with_context

from .pipeline import run
from .translator import SUPPORTED

ALLOWED_EXTENSIONS = {".mp3", ".wav", ".m4a", ".ogg", ".flac", ".webm"}
MAX_UPLOAD_MB = 100

app = Flask(__name__, template_folder="../../templates")
app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_MB * 1024 * 1024


def _allowed(filename: str) -> bool:
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS


@app.route("/")
def index():
    return render_template("index.html", languages=SUPPORTED)


@app.route("/transcribe", methods=["POST"])
def transcribe_route():
    audio = request.files.get("audio")
    target_lang = request.form.get("language", "es")
    model_size = request.form.get("model", "base")

    if not audio or not audio.filename:
        return {"error": "No audio file provided."}, 400
    if not _allowed(audio.filename):
        return {"error": f"Unsupported format. Allowed: {ALLOWED_EXTENSIONS}"}, 400
    if target_lang not in SUPPORTED:
        return {"error": f"Unknown language '{target_lang}'."}, 400

    suffix = Path(audio.filename).suffix.lower()
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        audio.save(tmp.name)
        tmp_path = tmp.name

    try:
        srt_content = run(tmp_path, target_lang=target_lang, model_size=model_size)
    except Exception as exc:
        return {"error": str(exc)}, 500
    finally:
        os.unlink(tmp_path)

    lang_name = SUPPORTED[target_lang]
    stem = Path(audio.filename).stem
    download_name = f"{stem}_{lang_name.lower()}.srt"

    return Response(
        srt_content,
        mimetype="text/plain",
        headers={
            "Content-Disposition": f'attachment; filename="{download_name}"',
            "X-Filename": download_name,
        },
    )


def create_app() -> Flask:
    return app

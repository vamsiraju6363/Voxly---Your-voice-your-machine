"""
Speech-to-text wrapper using OpenAI Whisper (base model).
Transcribes an audio file path and returns the text.
Keeps a warm model instance for fast repeated calls.
"""

import numpy as np
import whisper

# Lazy-loaded singleton so the model loads once at startup
_model = None


def _get_model() -> whisper.Whisper:
    """Load Whisper base model on first call, reuse after."""
    global _model
    if _model is None:
        _model = whisper.load_model("base")
    return _model


def transcribe_audio(file_path: str) -> str:
    """Transcribe an audio file using Whisper.

    Args:
        file_path: Path to an audio file in any format supported by Whisper/ffmpeg.

    Returns:
        Lowercased, stripped transcript (empty string if no speech detected).
    """
    model = _get_model()
    result = model.transcribe(file_path, fp16=False)
    return result["text"].strip()

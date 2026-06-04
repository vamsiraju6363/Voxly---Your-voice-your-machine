"""
Text-to-speech wrapper using Piper TTS.
Calls the Piper binary via subprocess to synthesize text → WAV bytes.
"""

import subprocess
import tempfile
import os
import shutil

# Path to the Piper binary (must be on PATH or absolute)
PIPER_BIN = shutil.which("piper") or "piper"

# Path to the Piper voice model (.onnx + .json)
# Download from: https://github.com/rhasspy/piper/releases
PIPER_MODEL = os.path.expanduser("~/.local/share/piper/en_US-lessac-medium.onnx")


def synthesize_speech(text: str) -> bytes:
    """Convert text to WAV audio bytes using Piper TTS.

    Args:
        text: Plain text to synthesize.

    Returns:
        WAV file contents as bytes.

    Raises:
        FileNotFoundError: Piper binary or voice model not found.
        RuntimeError:      Piper process failed.
    """
    if not os.path.isfile(PIPER_MODEL):
        raise FileNotFoundError(
            f"Piper voice model not found at {PIPER_MODEL}. "
            "Download it from https://github.com/rhasspy/piper/releases"
        )

    # Temporary file for the output WAV
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        out_path = tmp.name

    try:
        proc = subprocess.run(
            [PIPER_BIN, "--model", PIPER_MODEL, "--output_file", out_path],
            input=text,
            capture_output=True,
            text=True,
            timeout=30,
        )

        if proc.returncode != 0:
            raise RuntimeError(f"Piper TTS failed: {proc.stderr.strip()}")

        with open(out_path, "rb") as f:
            return f.read()

    finally:
        if os.path.isfile(out_path):
            os.unlink(out_path)

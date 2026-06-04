"""
Text-to-speech module using Coqui TTS (tacotron2-DDC model).
Synthesizes text into speech audio and plays it through the speakers.
"""

import os
import tempfile

import sounddevice as sd
import soundfile as sf
from TTS.api import TTS


class TextToSpeech:
    """Loads a Coqui TTS model and provides speak functionality."""

    def __init__(self, model_name: str = "tts_models/en/ljspeech/tacotron2-DDC"):
        """
        Args:
            model_name: Coqui TTS model identifier.
                        First run will download the model (~500 MB).
        """
        self.model = TTS(model_name=model_name)

    def synthesize(self, text: str) -> tuple:
        """Convert text to audio samples.

        Args:
            text: String to synthesize.

        Returns:
            Tuple of (audio_array: np.ndarray, sample_rate: int).
        """
        # Synthesize to a temporary file, then read back for playback
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            filepath = tmp.name

        self.model.tts_to_file(text=text, file_path=filepath)
        audio, sample_rate = sf.read(filepath)
        os.unlink(filepath)
        return audio, sample_rate

    def speak(self, text: str) -> None:
        """Synthesize text and immediately play it through the default speaker."""
        audio, sample_rate = self.synthesize(text)
        sd.play(audio, sample_rate)
        sd.wait()  # Block until playback finishes


# Standalone test: type text and hear it spoken
if __name__ == "__main__":
    print("Loading Coqui TTS model (first run will download ~500 MB)...")
    tts = TextToSpeech()
    print("Type text to speak (Ctrl+C to exit):\n")
    try:
        while True:
            user_input = input("Text: ")
            if user_input.strip():
                tts.speak(user_input.strip())
    except KeyboardInterrupt:
        print("\nGoodbye!")

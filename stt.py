"""
Speech-to-text module using OpenAI Whisper (base model) + sounddevice.
Records audio from the microphone and transcribes it to text.
"""

import numpy as np
import sounddevice as sd
import whisper


class SpeechToText:
    """Records audio via microphone and transcribes using Whisper."""

    def __init__(self, model_name: str = "base", sample_rate: int = 16000, duration: float = 5.0):
        """
        Args:
            model_name: Whisper model size (tiny, base, small, medium, large).
            sample_rate: Audio sample rate in Hz. Whisper expects 16kHz.
            duration: Recording length in seconds.
        """
        self.sample_rate = sample_rate
        self.duration = duration
        self.model = whisper.load_model(model_name)

    def record(self) -> np.ndarray:
        """Record audio from the default microphone for the configured duration.

        Returns:
            1-D numpy float32 array of audio samples in [-1, 1].
        """
        frames = int(self.duration * self.sample_rate)
        try:
            recording = sd.rec(frames, samplerate=self.sample_rate, channels=1, dtype="float32")
            sd.wait()  # Block until recording finishes
            return recording.flatten()
        except sd.PortAudioError as e:
            raise RuntimeError(f"Could not access microphone: {e}")

    def transcribe(self, audio: np.ndarray | None = None) -> str:
        """Transcribe audio to text.

        Args:
            audio: Optional pre-recorded audio array. Records fresh if None.

        Returns:
            Transcribed text string (empty if no speech detected).
        """
        if audio is None:
            audio = self.record()

        # Pass numpy float32 array directly to Whisper (avoids ffmpeg dependency)
        audio = audio.astype(np.float32)
        result = self.model.transcribe(audio, fp16=False)
        return result["text"].strip()


# Standalone test: record 5 seconds and print the transcription
if __name__ == "__main__":
    print("Loading Whisper base model (first run will download ~140 MB)...")
    stt = SpeechToText()
    print("Recording for 5 seconds — speak now!")
    try:
        text = stt.transcribe()
        print(f"Transcribed: {text if text else '(silence / no speech detected)'}")
    except RuntimeError as e:
        print(f"Error: {e}")

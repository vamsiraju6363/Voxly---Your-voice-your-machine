"""
Main voice-assistant loop: listen → transcribe → think → speak.
Runs 100% offline using Whisper (STT), Ollama (LLM), and Coqui TTS (TTS).
"""

import sys

from stt import SpeechToText
from llm import LLM
from tts import TextToSpeech


# Phrases that trigger a graceful exit
EXIT_PHRASES = {"goodbye", "goodbye.", "good bye", "good bye.", "bye", "bye.", "bye bye"}


def main() -> None:
    print("Initializing voice assistant (this may take a while on first run)...\n", flush=True)

    # --- Initialize Whisper ---
    try:
        stt = SpeechToText()
        print("[INIT] Whisper base model loaded.", flush=True)
    except Exception as e:
        print(f"[FATAL] Failed to load Whisper: {e}", flush=True)
        sys.exit(1)

    # --- Initialize Ollama ---
    try:
        chat = LLM()
        print("[INIT] Ollama client ready (ensure 'ollama serve' is running).", flush=True)
    except Exception as e:
        print(f"[FATAL] Failed to configure LLM: {e}", flush=True)
        sys.exit(1)

    # --- Initialize Coqui TTS ---
    try:
        tts = TextToSpeech()
        print("[INIT] Coqui TTS model loaded.", flush=True)
    except Exception as e:
        print(f"[FATAL] Failed to load TTS: {e}", flush=True)
        sys.exit(1)

    print("\nListening... (say 'goodbye' to exit, Ctrl+C to quit)\n", flush=True)

    try:
        while True:
            # -- Step 1: Record & transcribe --
            try:
                audio = stt.record()
                text = stt.transcribe(audio)
            except Exception as e:
                print(f"[STT ERROR] {e}", flush=True)
                continue

            # Skip empty transcriptions (silence / noise)
            if not text:
                continue

            print(f"[STT] {text}", flush=True)

            # Check for exit phrase
            if text.lower().strip() in EXIT_PHRASES:
                print("[LLM] Goodbye!", flush=True)
                try:
                    tts.speak("Goodbye!")
                except Exception:
                    pass
                break

            # -- Step 2: Get LLM response --
            try:
                reply = chat.send_message(text)
                print(f"[LLM] {reply}", flush=True)
            except Exception as e:
                print(f"[LLM ERROR] {e}", flush=True)
                continue

            # -- Step 3: Speak the reply --
            try:
                print("[TTS] Speaking...", flush=True)
                tts.speak(reply)
            except Exception as e:
                print(f"[TTS ERROR] {e}", flush=True)

    except KeyboardInterrupt:
        print("\nShutting down...", flush=True)

    print("Voice assistant stopped.", flush=True)


if __name__ == "__main__":
    main()

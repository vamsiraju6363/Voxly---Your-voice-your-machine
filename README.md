
# 🎙️ Voxly — Your Voice, Your Machine

<p align="center">
  <a href="https://github.com/vamsiraju6363/Voxly---Your-voice-your-machine">
    <img src="https://img.shields.io/badge/run%20on%20your%20machine-▶-blue?style=for-the-badge" alt="Run on your machine">
  </a>
  <br>
  <sup>Fully local · 100% offline · No API keys · No telemetry</sup>
</p>

A fully local, 100% offline voice assistant built in Python. Listens to your
mic, transcribes with Whisper, reasons with Ollama (Mistral 7B), and speaks
back with Coqui TTS. No API keys, no cloud, no telemetry.

---

## Architecture

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  stt.py  │ ──▶ │  llm.py  │ ──▶ │  tts.py  │ ──▶ │ speakers │
│  Whisper │     │  Ollama  │     │ CoquiTTS │     └──────────┘
│  (base)  │     │ (mistral)│     │(tacotron)│
└──────────┘     └──────────┘     └──────────┘
      ▲                                  │
      │         main.py loop             │
      └──────── listen → think → speak ──┘
```

---

## Quick Start

### Prerequisites

- **Python 3.10+**
- **Ollama** ([install](https://ollama.com/download/mac))
- **ffmpeg** `brew install ffmpeg` (macOS) or `apt install ffmpeg` (Linux)

### 1. Clone & install deps

```bash
git clone https://github.com/vamsiraju6363/Voxly---Your-voice-your-machine.git
cd Voxly---Your-voice-your-machine

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Start Ollama & pull the model (once)

```bash
# Terminal 1 — keep this running
ollama serve

# Terminal 2 — one-time model download (~4.4 GB)
ollama pull mistral
```

### 3. Launch the assistant

```bash
python main.py
```

The first run downloads Whisper base (~140 MB) and Tacotron2-DDC (~500 MB).
Subsequent launches are instant.

---

## Usage

| Action           | How                                |
| ---------------- | ---------------------------------- |
| Speak a command  | Wait for "Listening…" then talk    |
| Exit gracefully  | Say **"goodbye"**                  |
| Force quit       | Press **Ctrl+C**                   |

The console shows each stage:

```
[STT] what is the capital of France
[LLM] The capital of France is Paris.
[TTS] Speaking...
```

---

## Project Structure

| File               | Purpose                                         |
| ------------------ | ----------------------------------------------- |
| `main.py`          | Main loop: listen → transcribe → think → speak |
| `stt.py`           | Whisper wrapper — record mic, return text       |
| `llm.py`           | Ollama HTTP API wrapper with conversation memory|
| `tts.py`           | Coqui TTS wrapper — synthesize text to speech   |
| `requirements.txt` | Python dependencies (pinned minimum versions)   |

Each module is **independently testable**:
```bash
python stt.py   # Record 5s & transcribe
python llm.py   # Interactive text chat
python tts.py   # Type text & hear it spoken
```

---

## Configuration

| What                  | Where                    | Default                          |
| --------------------- | ------------------------ | -------------------------------- |
| Whisper model size    | `stt.py` → `model_name`  | `"base"` (also: tiny, small, …) |
| Recording duration    | `stt.py` → `duration`    | `5.0` seconds                    |
| Ollama model          | `llm.py` → `model`       | `"mistral"`                      |
| Ollama host           | `llm.py` → `host`        | `http://localhost:11434`         |
| System prompt         | `llm.py` → `SYSTEM_PROMPT`| Terse voice-assistant style     |
| TTS model             | `tts.py` → `model_name`  | `tts_models/en/ljspeech/tacotron2-DDC` |

---

## Troubleshooting

| Symptom                                    | Fix                                       |
| ------------------------------------------ | ----------------------------------------- |
| `ModuleNotFoundError: sounddevice`         | `pip install -r requirements.txt`         |
| `Could not connect to Ollama`              | Run `ollama serve` in another terminal    |
| `FileNotFoundError: ffmpeg`                | `brew install ffmpeg` / `apt install ffmpeg` |
| `PortAudioError` (no mic)                  | Check mic permissions in System Settings  |
| Ollama error 500 (missing `llama-server`)  | See [Ollama docs](https://github.com/ollama/ollama#building-from-source) |

---

## License

MIT — do whatever you want with it.

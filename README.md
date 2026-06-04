# 🎙️ Voxly — Your Voice, Your Machine

<p align="center">
  <sup>PC as server · Phone as client · 100% free · Cloudflare Tunnel</sup>
</p>

A voice assistant where your PC acts as the AI backend and your phone connects
to it from anywhere over a free Cloudflare Tunnel.

```
┌─────────────────────┐          ┌──────────────────────────────┐
│   Mobile (Expo)     │  HTTPS   │        Your PC (backend)      │
│                     │ ───────▶ │                                │
│  🎤 Press & hold   │  tunnel  │  Whisper → Ollama → Piper TTS │
│  🔊 Auto-playback  │ ◀─────── │  FastAPI on port 8000          │
└─────────────────────┘          └──────────────────────────────┘
```

---

## How It Works

1. **You speak** — press and hold the mic button on your phone
2. **Audio sent** via Cloudflare Tunnel to your PC
3. **PC transcribes** with Whisper, **thinks** with Ollama/Mistral, and
   **synthesizes speech** with Piper TTS
4. **Phone auto-plays** the assistant's spoken reply and shows the text

Everything is free. No API keys. No cloud subscriptions.

---

## Project Structure

```
voice-assistant/
├── backend/
│   ├── main.py           # FastAPI server — POST /chat endpoint
│   ├── stt.py            # Whisper base model wrapper
│   ├── llm.py            # Ollama client (per-session history)
│   ├── tts.py            # Piper TTS wrapper (subprocess)
│   ├── requirements.txt  # Python dependencies
│   └── start.sh          # Starts Ollama + FastAPI + Cloudflare Tunnel
├── mobile/
│   ├── App.js            # React Native UI — mic button + chat history
│   ├── api.js            # Sends audio to backend, receives WAV reply
│   ├── config.js         # Backend URL (paste your tunnel URL here)
│   ├── app.json          # Expo configuration
│   └── package.json      # Expo + React Native dependencies
└── README.md
```

---

## Setup Instructions

### Prerequisites

Install these on your **PC**:

| Tool              | Install                                                 |
| ----------------- | ------------------------------------------------------- |
| Python 3.10+      | https://python.org                                       |
| Ollama            | https://ollama.com/download                              |
| Piper TTS         | See [Piper install](#piper-tts-install) below            |
| cloudflared       | `brew install cloudflared` (macOS) or [download](https://github.com/cloudflare/cloudflared/releases) |
| ffmpeg            | `brew install ffmpeg` (macOS) / `apt install ffmpeg` (Linux) |
| Node.js 18+       | https://nodejs.org (for the mobile app)                  |

---

### 1. Backend Setup

```bash
# Clone the repo
git clone https://github.com/vamsiraju6363/Voxly---Your-voice-your-machine.git
cd Voxly---Your-voice-your-machine/backend

# Create virtual environment & install deps
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Pull the LLM model (one-time, ~4.4 GB)
ollama pull mistral
```

#### Piper TTS Install

```bash
# macOS
brew install piper

# Linux (download binary + voice model)
wget https://github.com/rhasspy/piper/releases/latest/download/piper_linux_x86_64.tar.gz
tar -xzf piper_linux_x86_64.tar.gz
sudo cp piper/piper /usr/local/bin/
```

Download the voice model:

```bash
mkdir -p ~/.local/share/piper
curl -L "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx" \
     -o ~/.local/share/piper/en_US-lessac-medium.onnx
curl -L "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json" \
     -o ~/.local/share/piper/en_US-lessac-medium.onnx.json
```

Test Piper:

```bash
echo "Hello world" | piper --model ~/.local/share/piper/en_US-lessac-medium.onnx --output_file test.wav
```

---

### 2. Launch the Backend

```bash
# From the backend/ directory
./start.sh
```

This starts three services in one terminal:
1. **Ollama** (port 11434)
2. **FastAPI** (port 8000)
3. **Cloudflare Tunnel** (exposes port 8000 publicly)

After a few seconds, the script prints a **public URL**:

```
╔══════════════════════════════════════════════╗
║   PUBLIC URL:  https://xxxx.trycloudflare.com
║   Set this in →  mobile/config.js
╚══════════════════════════════════════════════╝
```

**Copy this URL.** Press `Ctrl+C` to stop all services.

---

### 3. Mobile App Setup

```bash
# From the root of the repo
cd ../mobile
npm install
```

#### Configure the backend URL

Edit `mobile/config.js` and paste your Cloudflare Tunnel URL:

```js
export const API_URL = "https://xxxx.trycloudflare.com";
```

#### Run on your phone

```bash
npx expo start
```

This prints a QR code in the terminal. Scan it with:
- **iOS**: Camera app → tap the QR code → open in Expo Go
- **Android**: Expo Go app → Scan QR code

> Install the **Expo Go** app from the App Store / Play Store first.

---

## Usage

| Action           | How                                          |
| ---------------- | -------------------------------------------- |
| Speak a command  | Press & hold the mic button, release to send |
| See transcript   | Your words appear as a chat bubble           |
| Hear reply       | Auto-plays through phone speaker             |
| Multi-turn       | Session is maintained until you restart      |

---

## API Reference

### `POST /chat`

| Parameter     | Type     | In     | Description                           |
| ------------- | -------- | ------ | ------------------------------------- |
| `audio`       | file     | body   | Audio recording (WAV, MP3, M4A, etc.) |
| `session_id`  | string   | query  | Optional — reuse for conversation     |

**Response:** `audio/wav` with custom headers:

| Header           | Value                                  |
| ---------------- | -------------------------------------- |
| `X-Transcript`   | Transcribed text from your speech      |
| `X-Reply`        | Assistant's text reply                 |
| `X-Session-ID`   | UUID for continuing the conversation   |

---

## Configuration

| Setting               | File / Where                    | Default                               |
| --------------------- | ------------------------------- | ------------------------------------- |
| Whisper model         | `backend/stt.py` → `load_model` | `"base"` (also: tiny, small, medium) |
| Ollama model          | `backend/llm.py` → `MODEL_NAME` | `"mistral"`                           |
| System prompt         | `backend/main.py` → `SYSTEM_PROMPT` | Concise voice assistant style     |
| Piper voice model     | `backend/tts.py` → `PIPER_MODEL`| `en_US-lessac-medium`                 |
| FastAPI port          | `backend/start.sh` — uvicorn    | `8000`                                |
| Tunnel type           | `backend/start.sh` — cloudflared| Quick tunnel (trycloudflare.com)      |
| Backend URL (mobile)  | `mobile/config.js`              | Paste from terminal output            |

---

## Troubleshooting

| Symptom                                      | Fix                                                    |
| -------------------------------------------- | ------------------------------------------------------ |
| `Could not connect to Ollama`                | Run `ollama serve` in a terminal first                  |
| `Piper TTS failed` / `FileNotFoundError`     | Install Piper + download voice model (see above)        |
| `FileNotFoundError: ffmpeg`                  | `brew install ffmpeg` / `apt install ffmpeg`            |
| `No speech detected`                         | Check mic permissions on your phone                     |
| Cloudflare Tunnel URL not printed            | Make sure `cloudflared` is installed and on PATH        |
| App can't connect                            | Verify `config.js` has the correct URL                  |
| QR code not scanning                         | Make sure phone and PC are on different networks is OK  |
| Expo Go crashes on audio playback            | Update `expo-av` to latest version                      |

---

## License

MIT — do whatever you want with it.

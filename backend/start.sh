#!/usr/bin/env bash
# ============================================================
#  Voxly Backend Launcher
#  Starts Ollama + FastAPI + Cloudflare Tunnel together.
#  Press Ctrl+C to stop all services.
# ============================================================

set -e

cleanup() {
    echo ""
    echo "Shutting down..."
    kill $OLLAMA_PID 2>/dev/null || true
    kill $UVICORN_PID 2>/dev/null || true
    exit 0
}
trap cleanup SIGINT SIGTERM

# ---------- 1. Ollama ----------
echo "[1/3] Starting Ollama..."
ollama serve &
OLLAMA_PID=$!
sleep 3
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "WARNING: Ollama may not be ready yet. Continuing anyway..."
fi

# ---------- 2. FastAPI ----------
echo "[2/3] Starting FastAPI on http://localhost:8000 ..."
cd "$(dirname "$0")"
python -m uvicorn main:app --host 0.0.0.0 --port 8000 &
UVICORN_PID=$!
sleep 2

# ---------- 3. Cloudflare Tunnel ----------
echo "[3/3] Starting Cloudflare Tunnel..."
echo ""
echo "  ┌─────────────────────────────────────────────────┐"
echo "  │  Your public URL will appear below.             │"
echo "  │  Copy it into mobile/config.js as API_URL.      │"
echo "  └─────────────────────────────────────────────────┘"
echo ""

cloudflared tunnel --url http://localhost:8000 2>&1 | while IFS= read -r line; do
    echo "  $line"

    # Extract the trycloudflare URL from the log output
    if [[ "$line" =~ https://[a-zA-Z0-9.-]+\.trycloudflare\.com ]]; then
        URL=$(echo "$line" | grep -oE 'https://[a-zA-Z0-9.-]+\.trycloudflare\.com')
        echo ""
        echo "  ╔══════════════════════════════════════════════╗"
        echo "  ║                                              ║"
        echo "  ║   PUBLIC URL:  $URL"
        echo "  ║                                              ║"
        echo "  ║   Set this in →  mobile/config.js            ║"
        echo "  ║                                              ║"
        echo "  ╚══════════════════════════════════════════════╝"
        echo ""
    fi
done

cleanup

"""
FastAPI backend server for Voxly voice assistant.
Accepts audio via POST /chat, runs Whisper STT → Ollama LLM → Piper TTS,
and returns synthesized speech audio along with transcripts in headers.
"""

import uuid
import subprocess
import tempfile
import os
import atexit

from fastapi import FastAPI, UploadFile, File, Query, HTTPException
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from stt import transcribe_audio
from llm import get_llm_response
from tts import synthesize_speech

# --- System prompt injected into every new session ---
SYSTEM_PROMPT = (
    "You are a helpful voice assistant. "
    "Keep answers concise, under 3 sentences."
)

# --- In-memory session store: session_id → list of {role, content} dicts ---
sessions: dict[str, list[dict]] = {}

# --- FastAPI app ---
app = FastAPI(title="Voxly Voice Assistant", version="2.0.0")

# Allow requests from anywhere (frontend runs on phone / web)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/chat")
async def chat(
    audio: UploadFile = File(...),
    session_id: str | None = Query(default=None),
):
    """Main endpoint: audio in → reply audio out.

    Query params:
        session_id  – optional; reuse for multi-turn conversation

    Returns:
        WAV audio bytes with X-Transcript, X-Reply, X-Session-ID headers.
    """
    # --- Assign or create session ---
    if session_id is None or session_id not in sessions:
        session_id = str(uuid.uuid4())
        sessions[session_id] = [{"role": "system", "content": SYSTEM_PROMPT}]

    history = sessions[session_id]

    # --- Save uploaded audio to a temp file ---
    audio_bytes = await audio.read()
    ext = os.path.splitext(audio.filename or "audio.wav")[1] or ".wav"
    with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
        tmp.write(audio_bytes)
        input_path = tmp.name

    try:
        # --- 1. Speech-to-text ---
        transcript = transcribe_audio(input_path)
        if not transcript:
            raise HTTPException(status_code=400, detail="No speech detected")

        # --- 2. LLM response ---
        reply = get_llm_response(history, transcript)

        # --- 3. Text-to-speech ---
        audio_data = synthesize_speech(reply)

    finally:
        os.unlink(input_path)

    # --- Return WAV with metadata in headers ---
    return Response(
        content=audio_data,
        media_type="audio/wav",
        headers={
            "X-Transcript": transcript,
            "X-Reply": reply,
            "X-Session-ID": session_id,
        },
    )


@app.get("/health")
async def health():
    """Simple health-check endpoint."""
    return {"status": "ok", "sessions": len(sessions)}


# --- Entry point ---
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

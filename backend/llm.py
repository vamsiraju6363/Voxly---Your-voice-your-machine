"""
LLM client for Ollama's local HTTP API.
Manages per-session conversation history stored in the caller (FastAPI app).
"""

import json

import requests

OLLAMA_HOST = "http://localhost:11434"
MODEL_NAME = "mistral"


def get_llm_response(history: list[dict], user_text: str) -> str:
    """Send the user message to Ollama and return the assistant's reply.

    The history list is mutated in-place — the assistant's reply is appended
    so the next call in the same session carries full context.

    Args:
        history:   List of {"role": …, "content": …} dicts (system prompt included).
        user_text: The latest transcribed user message.

    Returns:
        The assistant's text reply.

    Raises:
        ConnectionError: Ollama server is unreachable.
        RuntimeError:    Malformed response from Ollama.
    """
    history.append({"role": "user", "content": user_text})

    payload = {
        "model": MODEL_NAME,
        "messages": history,
        "stream": False,
    }

    try:
        resp = requests.post(
            f"{OLLAMA_HOST}/api/chat",
            json=payload,
            timeout=60,
        )
        resp.raise_for_status()
        data = resp.json()
    except requests.exceptions.ConnectionError:
        raise ConnectionError(
            "Could not connect to Ollama. Make sure 'ollama serve' is running."
        )
    except requests.exceptions.Timeout:
        raise TimeoutError("Ollama request timed out. The model may still be loading.")
    except (KeyError, json.JSONDecodeError) as e:
        raise RuntimeError(f"Unexpected response from Ollama: {e}")

    reply = data["message"]["content"].strip()
    history.append({"role": "assistant", "content": reply})
    return reply

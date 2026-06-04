"""
LLM module for interacting with a local Ollama instance via its HTTP API.
Maintains conversation history and sends messages to the selected model.
"""

import json

import requests


class LLM:
    """Wraps the Ollama chat API and keeps a rolling conversation history."""

    SYSTEM_PROMPT = (
        "You are a helpful voice assistant. "
        "Keep answers short and conversational, under 3 sentences."
    )

    def __init__(self, model: str = "mistral", host: str = "http://localhost:11434"):
        """
        Args:
            model: Name of the Ollama model to use (e.g., mistral, llama3).
            host: Base URL of the Ollama server.
        """
        self.model = model
        self.host = host
        # Conversation history starts with the system prompt
        self.history: list[dict[str, str]] = [
            {"role": "system", "content": self.SYSTEM_PROMPT}
        ]

    def send_message(self, text: str) -> str:
        """Send a user message to Ollama and return the assistant's reply.

        Args:
            text: The user's message / transcribed speech.

        Returns:
            The assistant's text reply.

        Raises:
            ConnectionError: Ollama server is unreachable.
            RuntimeError: Unexpected or malformed response.
        """
        self.history.append({"role": "user", "content": text})

        payload = {
            "model": self.model,
            "messages": self.history,
            "stream": False,
        }

        try:
            resp = requests.post(
                f"{self.host}/api/chat",
                json=payload,
                timeout=60,
            )
            resp.raise_for_status()
            data = resp.json()
        except requests.exceptions.ConnectionError:
            raise ConnectionError(
                "Could not connect to Ollama. Is it running? Run 'ollama serve'."
            )
        except requests.exceptions.Timeout:
            raise TimeoutError("Ollama request timed out. The model may still be loading.")
        except (KeyError, json.JSONDecodeError) as e:
            raise RuntimeError(f"Unexpected response from Ollama: {e}")

        reply = data["message"]["content"].strip()
        self.history.append({"role": "assistant", "content": reply})
        return reply


# Standalone test: interactive chat in the terminal
if __name__ == "__main__":
    llm = LLM()
    print("Chat with Mistral (Ctrl+C to exit)")
    print("Make sure 'ollama serve' is running and 'mistral' model is pulled.\n")
    try:
        while True:
            user_input = input("You: ")
            if not user_input.strip():
                continue
            try:
                reply = llm.send_message(user_input)
                print(f"Assistant: {reply}\n")
            except (ConnectionError, TimeoutError, RuntimeError) as e:
                print(f"Error: {e}\n")
    except KeyboardInterrupt:
        print("\nGoodbye!")

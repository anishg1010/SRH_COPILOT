import os
import requests
from dotenv import load_dotenv

load_dotenv()


def generate_response(prompt: str, model: str | None = None) -> str:
    """Generate a response using Ollama."""
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    model_name = model or os.getenv("OLLAMA_MODEL", "llama3.1:8b")

    payload = {
        "model": model_name,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.2
        }
    }

    try:
        response = requests.post(f"{base_url}/api/generate", json=payload, timeout=120)
        response.raise_for_status()
        return response.json().get("response", "").strip()
    except requests.RequestException as exc:
        return (
            "Ollama request failed. Make sure Ollama is running and the model is installed.\n"
            f"Details: {exc}"
        )

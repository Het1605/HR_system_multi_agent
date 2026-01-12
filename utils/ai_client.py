# utils/ai_client.py
# Local Ollama AI client (NO payment, NO API key)
# This file ONLY talks to Ollama running on localhost.

import requests

OLLAMA_URL = "http://localhost:11434/api/chat"
OLLAMA_MODEL = "llama3.2"


def call_ollama(system_prompt, user_prompt):
    """
    Call local Ollama model and return AI response text.
    """

    payload = {
        "model": OLLAMA_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "stream": False
    }

    response = requests.post(
        OLLAMA_URL,
        json=payload,
        timeout=60
    )

    response.raise_for_status()

    data = response.json()
    return data["message"]["content"]
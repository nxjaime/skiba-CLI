"""OpenRouter API wrapper (minimal, self-contained).

- Reads API key from OPENROUTER_API_KEY env var.
- Base URL can be overridden via OPENROUTER_API_BASE.
- Provides balance fetch and chat completions.
"""

import os
import json
import time
import requests
from typing import List, Dict, Any

BASE = os.environ.get("OPENROUTER_API_BASE", "https://openrouter.ai/api")
API_KEY = os.environ.get("OPENROUTER_API_KEY", None)

HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}" if API_KEY else "",
}


def _req(path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    if not API_KEY:
        raise RuntimeError("OPENROUTER_API_KEY is not set in the environment.")
    url = BASE.rstrip("/") + "/v1/chat/completions"
    payload["model"] = payload.get("model")
    resp = requests.post(url, headers=HEADERS, json=payload, timeout=20)
    resp.raise_for_status()
    data = resp.json()
    return data


def chat(
    model: str,
    messages: List[Dict[str, str]],
    max_tokens: int = 1024,
    temperature: float = 0.2,
) -> Dict[str, Any]:
    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    data = _req("/v1/chat/completions", payload)
    return data


def balance() -> float:
    if not API_KEY:
        return 0.0
    url = BASE.rstrip("/") + "/v1/balance"
    resp = requests.get(url, headers=HEADERS, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    return float(data.get("balance", 0.0))

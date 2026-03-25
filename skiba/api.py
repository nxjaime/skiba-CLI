"""OpenRouter API wrapper (minimal, self-contained).

- Reads API key from OPENROUTER_API_KEY env var.
- Base URL can be overridden via OPENROUTER_API_BASE.
- Provides balance fetch and chat completions.
- Automatic retry with exponential backoff.
"""

import os
import json
import time
import random
import requests
from typing import List, Dict, Any

BASE = os.environ.get("OPENROUTER_API_BASE", "https://openrouter.ai/api")
API_KEY = os.environ.get("OPENROUTER_API_KEY", None)

HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}" if API_KEY else "",
}

# Retry configuration
MAX_RETRIES = int(os.environ.get("OPENROUTER_MAX_RETRIES", "3"))
INITIAL_DELAY = float(os.environ.get("OPENROUTER_INITIAL_DELAY", "1.0"))
MAX_DELAY = float(os.environ.get("OPENROUTER_MAX_DELAY", "10.0"))
BACKOFF_FACTOR = float(os.environ.get("OPENROUTER_BACKOFF_FACTOR", "2.0"))


def _should_retry(response: requests.Response) -> bool:
    """Determine if the response is retryable."""
    if response is None:
        return True  # network-level failure
    code = response.status_code
    # Retry on rate limit (429) and server errors (5xx)
    return code == 429 or (500 <= code < 600)


def _sleep_with_jitter(delay: float) -> None:
    """Sleep for delay + random jitter to avoid thundering herd."""
    jitter = random.uniform(0, 0.1 * delay)
    time.sleep(delay + jitter)


def _req(path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    if not API_KEY:
        raise RuntimeError("OPENROUTER_API_KEY is not set in the environment.")
    url = BASE.rstrip("/") + "/v1/chat/completions"
    payload["model"] = payload.get("model")

    delay = INITIAL_DELAY
    last_exc = None
    last_resp = None

    for attempt in range(MAX_RETRIES + 1):
        try:
            resp = requests.post(url, headers=HEADERS, json=payload, timeout=20)
            last_resp = resp
            if resp.status_code == 200:
                return resp.json()
            if not _should_retry(resp):
                resp.raise_for_status()
        except (requests.RequestException, json.JSONDecodeError) as e:
            last_exc = e

        if attempt < MAX_RETRIES:
            _sleep_with_jitter(delay)
            delay = min(delay * BACKOFF_FACTOR, MAX_DELAY)
        else:
            break

    # Build a helpful error message
    if last_resp is not None:
        try:
            detail = last_resp.json().get("error", last_resp.text)
        except Exception:
            detail = last_resp.text
        raise RuntimeError(
            f"OpenRouter request failed after {MAX_RETRIES} retries: {last_resp.status_code} - {detail}"
        )
    else:
        raise RuntimeError(
            f"OpenRouter request failed after {MAX_RETRIES} retries: {last_exc}"
        ) from last_exc


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
    return _req("/v1/chat/completions", payload)


def balance() -> float:
    if not API_KEY:
        return 0.0
    url = BASE.rstrip("/") + "/v1/balance"
    # Balance calls are simple GET; add same retry pattern
    delay = INITIAL_DELAY
    last_exc = None
    last_resp = None
    for attempt in range(MAX_RETRIES + 1):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=10)
            last_resp = resp
            if resp.status_code == 200:
                return float(resp.json().get("balance", 0.0))
            if not _should_retry(resp):
                resp.raise_for_status()
        except (requests.RequestException, ValueError) as e:
            last_exc = e

        if attempt < MAX_RETRIES:
            _sleep_with_jitter(delay)
            delay = min(delay * BACKOFF_FACTOR, MAX_DELAY)
        else:
            break

    if last_resp is not None:
        try:
            detail = last_resp.json().get("error", last_resp.text)
        except Exception:
            detail = last_resp.text
        raise RuntimeError(
            f"OpenRouter balance check failed after {MAX_RETRIES} retries: {last_resp.status_code} - {detail}"
        )
    else:
        raise RuntimeError(
            f"OpenRouter balance check failed after {MAX_RETRIES} retries: {last_exc}"
        ) from last_exc

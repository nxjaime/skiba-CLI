"""Dynamic routing engine to select model based on prompt context."""

import os
import re
from typing import Tuple

OPENROUTER_MODELS = {
    "minimax": os.environ.get("OPENROUTER_MODEL_MINIMAX", "minimax/minimax"),
    "claude_sonnet": os.environ.get(
        "OPENROUTER_MODEL_SONNET", "anthropic/claude-sonnet-4"
    ),
    "gemini_flash": os.environ.get(
        "OPENROUTER_MODEL_GEMINI", "google/gemini-flash-1.5"
    ),
}


def estimate_tokens(text: str) -> int:
    return max(1, int(len(text) / 4))


def classify_task(prompt: str) -> str:
    t = prompt.lower()
    if any(w in t for w in ["design", "architecture", "refactor", "system", "scala"]):
        return "architectural"
    if any(w in t for w in ["debug", "trace", "log", "error"]):
        return "debug"
    if any(w in t for w in ["summary", "explain"]):
        return "summary"
    if len(t) > 800:
        return "extensive"
    return "standard"


def route_model(prompt: str, est_tokens: int, balance: float) -> Tuple[str, int]:
    model_key = "minimax"
    task = classify_task(prompt)
    if task in ("architectural", "debug", "extensive"):
        model_key = "claude_sonnet"
    if est_tokens > 8000:
        model_key = "gemini_flash"
    if balance is not None and balance < 0.01:
        model_key = "minimax"
    model = OPENROUTER_MODELS.get(model_key, OPENROUTER_MODELS["minimax"])
    return model, est_tokens

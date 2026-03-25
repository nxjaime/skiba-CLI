"""Dynamic routing engine to select model based on prompt context."""

import re
from typing import Tuple


def estimate_tokens(text: str) -> int:
    # Very rough estimator: 1 token ~ 4 characters; ensure at least 1
    return max(1, int(len(text) / 4))


def classify_task(prompt: str) -> str:
    # Very lightweight heuristic to gauge complexity
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
    # Default to minimax (low-cost)
    model = "minimax"
    # Heuristics to move to more capable models
    task = classify_task(prompt)
    if task in ("architectural", "debug", "extensive"):
        model = "claude_sonnet"
    if est_tokens > 8000:
        model = "gemini_flash"
    # Budget guard: if balance low, force cheaper model
    if balance is not None and balance < 0.01:
        model = "minimax"
    return model, est_tokens

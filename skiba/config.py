import json
import os
from pathlib import Path

"""Configuration management for Skiba.

- Stores budget, context limits, and history preference in ~/.skiba/config.json
- Exposes small helpers to load/save the config.
"""

CONFIG_PATH = Path.home() / ".skiba_config.json"

DEFAULT = {
    "budget_per_prompt": 0.50,  # USD per prompt as a soft cap
    "max_tokens_per_prompt": 2048,
    "context_limit_tokens": 4096,
    "include_history": True,
    "verbosity": 1,
}


def load_config() -> dict:
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return DEFAULT.copy()


def save_config(cfg: dict) -> None:
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2)
    except Exception:
        pass

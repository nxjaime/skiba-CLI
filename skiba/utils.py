import os
from pathlib import Path
from typing import List

from .tokens import count_tokens


def read_files(paths: List[str], limit: int) -> str:
    """Read files and concatenate their contents, respecting a token limit."""
    parts = []
    total = 0
    for p in paths:
        try:
            with open(p, "r", encoding="utf-8") as f:
                data = f.read()
                est = count_tokens(data)
                if total + est > limit:
                    break
                parts.append(data)
                total += est
        except Exception:
            continue
    return "\n---\n".join(parts)

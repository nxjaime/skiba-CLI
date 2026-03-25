import os
from pathlib import Path
from typing import List


def read_files(paths: List[str], limit: int) -> str:
    """Read files and concatenate their contents, respecting a rough token limit."""
    parts = []
    total = 0
    for p in paths:
        try:
            with open(p, "r", encoding="utf-8") as f:
                data = f.read()
                # crude token estimate: characters / 4
                est = max(1, len(data) // 4)
                if total + est > limit:
                    break
                parts.append(data)
                total += est
        except Exception:
            continue
    return "\n---\n".join(parts)

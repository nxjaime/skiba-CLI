from typing import Dict


def render_receipt(token_prompt: int, token_completion: int, cost: float) -> str:
    parts = [
        f"Prompt tokens: {token_prompt}",
        f"Completion tokens: {token_completion}",
        f"Cost: ${cost:.6f}",
    ]
    return ", ".join(parts)

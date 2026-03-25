"""Cost estimation utilities for OpenRouter models.
We model costs as tokens-based; the real OpenRouter pricing may differ.
"""

from typing import Dict

# Cost per 1k tokens in USD for named models (example numbers)
MODEL_COSTS_PER_1K = {
    "minimax": 0.10,  # low-cost, default for standard prompts
    "claude_sonnet": 0.60,  # complex tasks
    "gemini_flash": 1.20,  # massive context windows
}


def cost_for(model: str, tokens_prompt: int, tokens_completion: int) -> float:
    per_1k = MODEL_COSTS_PER_1K.get(model, MODEL_COSTS_PER_1K["minimax"])
    total_tokens = max(0, tokens_prompt + tokens_completion)
    # cost per token approximated as per_1k / 1000
    return (total_tokens / 1000.0) * per_1k


def format_cost(cost: float) -> str:
    return f"${cost:.6f}"

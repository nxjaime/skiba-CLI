"""Helper for constructing messages payloads for the OpenRouter API."""

from typing import List, Dict


def build_messages(
    user_prompt: str, history: List[Dict[str, str]] = None
) -> List[Dict[str, str]]:
    messages = []
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": user_prompt})
    return messages

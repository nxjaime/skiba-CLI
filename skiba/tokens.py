"""Token counting utilities.

- Tries to use tiktoken for accurate counts.
- Falls back to a simple character estimator if tiktoken is unavailable or model not recognized.
"""

try:
    import tiktoken

    # Use cl100k_base as a generic tokenizer (covers OpenAI, Anthropic, Google, etc.)
    _enc = tiktoken.get_encoding("cl100k_base")

    def count_tokens(text: str) -> int:
        """Count tokens accurately using tiktoken."""
        return len(_enc.encode(text))

except Exception:
    # tiktoken not installed or encoding not available
    def count_tokens(text: str) -> int:
        """Fallback estimator: 1 token ~ 4 characters."""
        return max(1, len(text) // 4)

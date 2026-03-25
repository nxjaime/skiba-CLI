"""Unit tests for token counting."""

import pytest
from skiba.tokens import count_tokens


def test_english_hello_world():
    assert count_tokens("Hello world!") > 0


def test_longer_text():
    text = "Skiba is a modular Python CLI coding assistant."
    tokens = count_tokens(text)
    assert tokens > 0
    assert tokens < len(text) // 3  # not more than 1 per 3 chars


def test_empty():
    assert count_tokens("") == 0

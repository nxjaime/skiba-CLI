"""Unit tests for the routing engine."""

import pytest
from skiba.router import route_model, classify_task, estimate_tokens


def test_estimate_tokens_non_empty():
    assert estimate_tokens("hello") > 0


def test_classify_task_standard():
    prompt = "What time is it?"
    assert classify_task(prompt) == "standard"


def test_classify_task_debug():
    prompt = "debug the error in the stack trace"
    assert classify_task(prompt) == "debug"


def test_classify_task_architectural():
    prompt = "design a system for scaling to millions of users"
    assert classify_task(prompt) == "architectural"


def test_classify_task_extensive():
    prompt = (
        "This is a very long technical documentation with lots of details about "
        + ("x" * 1000)
    )
    assert classify_task(prompt) == "extensive"


def test_route_model_short_uses_minimax():
    model, tokens = route_model("hello", 1, 100.0)
    assert "minimax" in model.lower()


def test_route_model_debug_uses_sonnet():
    model, tokens = route_model("debug the error", 100, 100.0)
    assert "claude" in model.lower()


def test_route_model_large_uses_gemini():
    large_prompt = "x" * 40000  # ~10k tokens
    model, tokens = route_model(large_prompt, 10000, 100.0)
    assert "gemini" in model.lower()


def test_route_model_low_balance_forces_minimax():
    model, tokens = route_model("complex debugging task", 500, 0.001)
    assert "minimax" in model.lower()

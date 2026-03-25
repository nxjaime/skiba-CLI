"""Unit tests for cost estimation."""

import pytest
from skiba.cost import cost_for, format_cost


def test_cost_for_minimax():
    cost = cost_for("minimax/minimax", 100, 50)
    assert cost > 0


def test_cost_for_claude_sonnet():
    cost = cost_for("anthropic/claude-sonnet-4", 100, 50)
    assert cost > 0


def test_cost_for_unknown_model():
    # Falls back to minimax pricing
    cost = cost_for("unknown/model", 100, 50)
    assert cost > 0


def test_format_cost():
    formatted = format_cost(0.1234567)
    assert formatted.startswith("$")
    assert "0.123" in formatted


def test_cost_proportional_to_tokens():
    cost1 = cost_for("minimax/minimax", 100, 50)
    cost2 = cost_for("minimax/minimax", 200, 100)
    assert cost2 > cost1

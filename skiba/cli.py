#!/usr/bin/env python3
"""Skiba CLI: modular, OpenRouter-backed coding assistant."""

import argparse
import json
import os
from typing import List, Dict

from . import __version__ as __ver
from .config import load_config, save_config
from .api import balance as api_balance, chat
from .cost import cost_for, format_cost
from .router import route_model, estimate_tokens
from .prompt_builders import build_messages
from .receipts import render_receipt
from .utils import read_files

try:
    # Lazy import to avoid import-time side effects if skill system isn't used in tests
    from .skills import load_skills

    SKILLS = load_skills()
except Exception:
    SKILLS = {}

CONTEXT_READ_FILES = []  # can be extended via CLI later


def _print_balance():
    try:
        bal = api_balance()
        print(f"OpenRouter balance: ${bal:.6f}")
    except Exception:
        print("OpenRouter balance: unavailable (check API key)")


def run_prompt(prompt: str, paths: List[str], cfg: Dict[str, object]):
    # Read local files into context
    context_limit = int(cfg.get("context_limit_tokens", 4096))
    local_ctx = read_files(paths, limit=context_limit) if paths else ""
    full_prompt = prompt + ("\n" + local_ctx if local_ctx else "")

    est_tokens = estimate_tokens(full_prompt)
    bal = 0.0
    try:
        bal = api_balance()
    except Exception:
        bal = 0.0

    model, tokens_to_consider = route_model(full_prompt, est_tokens, bal)
    max_tokens = int(cfg.get("max_tokens_per_prompt", 2048))
    if max_tokens < tokens_to_consider:
        max_tokens = tokens_to_consider

    # Build messages
    messages = [{"role": "user", "content": full_prompt}]
    try:
        res = chat(model, messages, max_tokens=max_tokens, temperature=0.2)
    except Exception:
        # Fallback to minimax if primary fails
        model = "minimax"
        res = chat(model, messages, max_tokens=max_tokens, temperature=0.2)

    # Parse response and usage
    content = (
        "".join(
            [c.get("message", {}).get("content", "") for c in res.get("choices", [])]
        )
        if isinstance(res, dict)
        else ""
    )
    usage = res.get("usage", {}) if isinstance(res, dict) else {}
    prompt_tokens = int(usage.get("prompt_tokens", est_tokens))
    completion_tokens = int(usage.get("completion_tokens", max_tokens))
    total_cost = 0.0
    try:
        total_cost = cost_for(model, prompt_tokens, completion_tokens)
    except Exception:
        total_cost = 0.0

    print(content)
    receipt = render_receipt(prompt_tokens, completion_tokens, total_cost)
    print("\nReceipt:", receipt)

    # Simple history persistence if enabled
    if cfg.get("include_history", True):
        pass  # could append to a session history log


def main():
    parser = argparse.ArgumentParser(
        prog="skiba", description="OpenRouter-backed modular coding assistant"
    )
    subparsers = parser.add_subparsers(dest="command", required=False)

    # Top-level run command
    run_p = subparsers.add_parser("run", help="Run a prompt through the routing engine")
    run_p.add_argument("prompt", nargs="?", help="Prompt to solve", default="")
    run_p.add_argument(
        "paths", nargs="*", help="Local file paths to include as context", default=[]
    )
    run_p.add_argument(
        "-l", "--lang", dest="lang", help="Force output language (e.g., en, fr)"
    )
    run_p.add_argument(
        "--set-budget",
        dest="budget",
        type=float,
        help="Override per-prompt budget (USD)",
    )
    run_p.add_argument(
        "--set-tokens", dest="tokens", type=int, help="Override max tokens per prompt"
    )
    run_p.add_argument(
        "--no-history",
        dest="no_history",
        action="store_true",
        help="Disable history for this request",
    )
    run_p.add_argument(
        "--verbose", action="store_true", help="Increase debug verbosity"
    )

    # Simple config commands
    cfg_p = subparsers.add_parser("config", help="View or set configuration")
    cfg_p.add_argument(
        "key",
        nargs="?",
        help="Config key to set/view (budget_per_prompt, max_tokens_per_prompt, context_limit_tokens, include_history)",
    )
    cfg_p.add_argument("value", nargs="?", help="Value for the given key")

    args = parser.parse_args()
    cfg = load_config()

    if args.command == "config" and args.key:
        if args.value is None:
            print(json.dumps(cfg, indent=2))
        else:
            # simple set path
            cfg[args.key] = type(cfg.get(args.key, ""))(args.value)  # naive cast
            save_config(cfg)
            print(f"Set {args.key} = {args.value}")
        return

    if args.command == "run":
        prompt = args.prompt
        if not prompt:
            prompt = input("Enter prompt: ")
        cfg.setdefault("context_limit_tokens", 4096)
        if args.no_history:
            cfg["include_history"] = False
        if args.budget is not None:
            cfg["budget_per_prompt"] = args.budget
        if args.tokens is not None:
            cfg["max_tokens_per_prompt"] = args.tokens
        # Update language default if provided (not used heavily in this minimal impl)
        if args.lang:
            cfg["lang"] = args.lang
        save_config(cfg)
        # Run the prompt
        run_prompt(prompt, list(args.paths), cfg)
        return

    # Default behavior: show balance at startup and explain hidden behaviors
    _print_balance()
    print("Skiba ready. Use 'skiba run <prompt>' to execute a prompt.")


if __name__ == "__main__":  # pragma: no cover
    main()

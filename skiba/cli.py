#!/usr/bin/env python3
"""Skiba CLI: modular, OpenRouter-backed coding assistant with Claude Code-like UI."""

import argparse
import sys
from typing import List, Dict

from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel
from rich.spinner import Spinner
from rich.theme import Theme

from . import __version__ as __ver
from .config import load_config, save_config
from .api import balance as api_balance, chat
from .cost import cost_for
from .router import route_model, estimate_tokens
from .receipts import render_receipt
from .utils import read_files

console = Console(
    theme=Theme(
        {
            "info": "bold bright_red",
            "warning": "bright_red",
            "error": "bold white",
            "user": "bold white",
            "assistant": "white",
            "accent": "bright_red",
            "muted": "dim white",
        }
    )
)

BANNER = """[bright_red]
╔═╗╦ ╦╔═╗╔═╗╔═╗  ╔╦╗╦ ╦╔═╗  ╔╦╗╦ ╦╔═╗╔═╗╔═╗[/bright_red]
[bold bright_red]║ ╦║ ║║╣ ╚═╗╚═╗   ║ ╠═╣║╣   ║║║║ ║║╣ ╚═╗╚═╗[/bold bright_red]
[bold red]╚═╝╚═╝╚═╝╚═╝╚═╝   ╩ ╩ ╩╚═╝  ═╩╝╚═╝╚═╝╚═╝╚═╝[/bold red]"""
SUBTITLE = "[dim white]OpenRouter · AI Coding Assistant[/dim white]"


def print_banner():
    console.print(BANNER)
    console.print(SUBTITLE, justify="center")
    console.print()


def print_balance():
    try:
        bal = api_balance()
        console.print(f"[info]Balance:[/info] [accent]${bal:.4f}[/accent]")
    except Exception:
        console.print("[error]OpenRouter balance unavailable[/error] (check API key)")


def run_prompt(prompt: str, paths: List[str], cfg: Dict) -> bool:
    context_limit = int(cfg.get("context_limit_tokens", 4096))
    local_ctx = read_files(paths, limit=context_limit) if paths else ""
    full_prompt = prompt + (
        "\n\n[Context from files]\n" + local_ctx if local_ctx else ""
    )

    est_tokens = estimate_tokens(full_prompt)
    try:
        bal = api_balance()
    except Exception:
        bal = 0.0

    model, _ = route_model(full_prompt, est_tokens, bal)
    max_tokens = int(cfg.get("max_tokens_per_prompt", 2048))

    console.print(f"[muted]Model:[/muted] [accent]{model.upper()}[/accent]")
    console.print(f"[muted]Tokens:[/muted] [accent]~{est_tokens}[/accent]")
    console.print()

    with Live(
        Spinner("point", text="Thinking...", style="bright_red"),
        console=console,
        transient=True,
        refresh_per_second=12,
    ):
        try:
            res = chat(
                model, [{"role": "user", "content": full_prompt}], max_tokens=max_tokens
            )
        except Exception as e:
            console.print(f"\n[error]Model error:[/error] {e}")
            console.print("[muted]Falling back to minimax...[/muted]")
            model = "minimax"
            try:
                res = chat(
                    model,
                    [{"role": "user", "content": full_prompt}],
                    max_tokens=max_tokens,
                )
            except Exception as e2:
                console.print(f"\n[error]Fatal:[/error] {e2}")
                return False

    content = ""
    if isinstance(res, dict):
        content = "".join(
            c.get("message", {}).get("content", "") for c in res.get("choices", [])
        )
    usage = res.get("usage", {}) if isinstance(res, dict) else {}
    prompt_tokens = int(usage.get("prompt_tokens", est_tokens))
    completion_tokens = int(usage.get("completion_tokens", 0))
    total_cost = cost_for(model, prompt_tokens, completion_tokens)

    receipt_text = render_receipt(prompt_tokens, completion_tokens, total_cost)
    console.print()
    console.print(
        Panel(
            "[assistant]" + content,
            title="Response",
            border_style="bright_red",
            expand=False,
        )
    )
    console.print()
    console.print(f"[muted]│[/muted] [muted]{receipt_text}[/muted]")
    return True


def interactive_mode(cfg: Dict):
    console.print(
        "[info]Entering interactive mode. Type 'exit' or Ctrl+C to quit.[/info]"
    )
    console.print()
    history = []
    while True:
        try:
            user_input = console.input("\n[user]➜[/user] ")
            if user_input.strip().lower() in ("exit", "quit", "q"):
                console.print("[info]Goodbye![/info]")
                break
            if not user_input.strip():
                continue
            history.append({"role": "user", "content": user_input})
            success = run_prompt(user_input, [], cfg)
            if success:
                console.print()
                console.print("[muted]─" * 40)
        except (KeyboardInterrupt, EOFError):
            console.print("\n[info]Goodbye![/info]")
            break


def main():
    parser = argparse.ArgumentParser(
        prog="skiba", description="OpenRouter-backed AI coding assistant"
    )
    subparsers = parser.add_subparsers(dest="command", required=False)

    run_p = subparsers.add_parser("run", help="Run a prompt")
    run_p.add_argument("prompt", nargs="?", help="Prompt to execute", default="")
    run_p.add_argument("paths", nargs="*", help="Local files as context", default=[])
    run_p.add_argument("-l", "--lang", dest="lang", help="Force output language")
    run_p.add_argument(
        "--set-budget", dest="budget", type=float, help="Per-prompt budget (USD)"
    )
    run_p.add_argument(
        "--set-tokens", dest="tokens", type=int, help="Max tokens per prompt"
    )
    run_p.add_argument(
        "--no-history", dest="no_history", action="store_true", help="Disable history"
    )
    run_p.add_argument(
        "-y", "--yes", dest="yes", action="store_true", help="Skip confirmation"
    )

    subparsers.add_parser("interactive", help="Start interactive mode")
    subparsers.add_parser("balance", help="Check OpenRouter balance")

    cfg_p = subparsers.add_parser("config", help="View or set configuration")
    cfg_p.add_argument("key", nargs="?", help="Config key")
    cfg_p.add_argument("value", nargs="?", help="Value to set")

    args = parser.parse_args()
    cfg = load_config()

    if args.command == "balance":
        print_banner()
        print_balance()
        return

    if args.command == "config":
        if args.key:
            if args.value is None:
                import json

                console.print_json(json.dumps(cfg, indent=2))
            else:
                cfg[args.key] = type(cfg.get(args.key, ""))(args.value)
                save_config(cfg)
                console.print(f"[accent]✓[/accent] Set {args.key} = {args.value}")
        else:
            import json

            console.print_json(json.dumps(cfg, indent=2))
        return

    if args.command == "interactive":
        print_banner()
        print_balance()
        console.print()
        interactive_mode(cfg)
        return

    if args.command == "run":
        prompt = args.prompt
        if not prompt:
            prompt = console.input("\n[user]➜[/user] ")
        cfg.setdefault("context_limit_tokens", 4096)
        if args.no_history:
            cfg["include_history"] = False
        if args.budget is not None:
            cfg["budget_per_prompt"] = args.budget
        if args.tokens is not None:
            cfg["max_tokens_per_prompt"] = args.tokens
        save_config(cfg)
        console.print()
        success = run_prompt(prompt, list(args.paths), cfg)
        sys.exit(0 if success else 1)

    print_banner()
    print_balance()
    console.print()
    console.print("[info]Usage:[/info]")
    console.print(
        '  [accent]skiba run "your prompt"[/accent]          Run a single prompt'
    )
    console.print(
        '  [accent]skiba run "prompt" file.py file2.md[/accent] Run with file context'
    )
    console.print(
        "  [accent]skiba interactive[/accent]                  Start interactive mode"
    )
    console.print("  [accent]skiba balance[/accent]                      Check balance")
    console.print("  [accent]skiba config[/accent]                       View config")
    console.print()


if __name__ == "__main__":
    main()

# Skiba — OpenRouter-powered Python CLI Assistant

Skiba is a modular CLI tool designed to route prompts to OpenRouter models based on task complexity, context, and cost.

- Default routing uses low-cost MiniMax for standard prompts.
- Complex tasks auto-route to Claude Sonnet.
- Very large contexts route to Gemini Flash.
- Includes a plugin/skill system for extensibility.

Prerequisites:
- OPENROUTER_API_KEY environment variable set.
- Optional: OPENROUTER_API_BASE for custom OpenRouter deployments.

Run:
- Set up: python -m skiba.cli run "Your prompt here" path/to/context.txt
- View/adjust config: python -m skiba.cli config

See code in the skiba/ directory for implementation details.

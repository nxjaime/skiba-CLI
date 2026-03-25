# Skiba CLI - 30-Sprint Roadmap

**Project**: Skiba - Modular OpenRouter CLI Assistant  
**Status**: Sprints 1-3 Complete ✅  
**Timeline**: 30 sprints (~60 weeks at 2-week sprints)  
**Last Updated**: 2025-06-24

---

## Sprint Overview

### Phase 1: Foundation & Reliability (Sprints 1-5)
**Goal**: Stabilize the core, add resilience, establish testing culture.

| Sprint | Title | User Stories | Acceptance Criteria | Status |
|--------|-------|--------------|---------------------|--------|
| 1 | Retry & Resilience | As a user, I want transient API failures to auto-retry so my prompts don't fail on network hiccups. | • Exponential backoff with jitter on 429/5xx/4xx<br>• Max 3 retries, configurable<br>• Clear fallback notification | ✅ DONE |
| 2 | Real Token Counting | As a user, I want accurate token estimates so costs are predictable. | • Use `tiktoken` for OpenAI‑style models<br>• Fallback to char/4 for others<br>• Show token estimate before execution (with flag) | ✅ DONE |
| 3 | Unit Test Coverage | As a developer, I want tests for routing, cost, and utils so I can refactor safely. | • 80%+ coverage on router, cost, utils<br>• fixtures for mock API responses<br>• CI runs on push | ✅ DONE |
| 4 | Structured Logging | As an operator, I want JSON logs so I can monitor in production. | • `logging` module with `--debug`/`--json` flags<br>• No API keys in logs<br>• Separate error/usage/telemetry logs |
| 5 | Config Validation | As a user, I want config typos to be caught early. | • Pydantic schema for config<br>• Auto‑migration on version bumps<br>• `skiba config validate` command |

---

### Phase 2: Cost & Routing (Sprints 6-10)
**Goal**: Accurate cost tracking, intelligent routing, budget guardrails.

| Sprint | Title | User Stories | Acceptance Criteria |
|--------|-------|--------------|--------------------|
| 6 | Dynamic Pricing Sync | As a user, I want real‑time model pricing so I'm not overcharged. | • Daily fetch of `/api/v1/models`<br>• Cache to `~/.skiba/models.json`<br>• Map model IDs → cost/1k automatically |
| 7 | Context‑Aware Routing | As a user, I want the CLI to pick the cheapest model that fits my task. | • If tokens > 4k → gemini‑flash<br>• If task = debug/arch → claude‑sonnet (if budget allows)<br>• Else minimax |
| 8 | Budget Enforcement | As a cost‑conscious user, I want prompts that exceed my budget to be rejected or downgraded. | • Pre‑flight cost estimate<br>• If > budget, halve tokens and retry cheaper model<br>• Add `--strict` to hard‑fail |
| 9 | Session Cost Tracking | As a user, I want per‑session cost totals so I know my spend. | • SQLite DB `~/.skiba/sessions.db`<br>• Each `run` logs tokens, cost, model, timestamp<br>• `skiba session` shows summary |
| 10 | Model Override CLI | As a power user, I want to force a specific model for a prompt. | • `--model <id>` flag on `run`<br>• Validation against OpenRouter catalog<br>• Override budget checks (with warning) |

---

### Phase 3: Skills & Tools (Sprints 11-15)
**Goal**: Make skills/plugins functional, not just loaded.

| Sprint | Title | User Stories | Acceptance Criteria |
|--------|-------|--------------|--------------------|
| 11 | Tool Schema Registry | As a developer, I want to declare tools with JSON schemas so the LLM can call them. | • `Skill.input_schema` dict<br>• `Skill.run(**kwargs)` signature<br>• Registry exposes list of tools |
| 12 | Function Calling Adapter | As a user, I want the LLM to use tools automatically when needed. | • Build OpenAI‑compatible `tools` payload from skill schemas<br>• Parse `tool_calls` in response<br>• Execute skill, feed result back (auto‑loop) |
| 13 | Approval Flow | As a cautious user, I want to confirm destructive tool calls. | • `skill_policy` config (auto/confirm/disabled)<br>• Interactive prompt for write actions<br>• Log tool use in session |
| 14 | Skill Packaging | As a contributor, I want to publish skills as PyPI packages. | • Entry point `skiba_skills` auto‑discovery<br>• Dependency‑injection pattern<br>• `skiba skills install <pkg>` |
| 15 | Built‑in Skills | As a user, I want useful built‑in skills out of the box. | • `read_file` (read arbitrary local file with limits)<br>• `grep` (search files)<br>• `shell` (run safe commands with confirmation) |

---

### Phase 4: Interactive Experience (Sprints 16-20)
**Goal**: Make interactivity feel like a proper chat IDE.

| Sprint | Title | User Stories | Acceptance Criteria |
|--------|-------|--------------|--------------------|
| 16 | Streaming Output | As a user, I want to see assistant responses as they generate. | • SSE/streaming from OpenRouter<br>• Rich `Live` panel updates word‑by‑word<br>• User can cancel generation with Ctrl+C |
| 17 | Edit Last Response | As a user, I want to edit the assistant's last answer in my editor. | • `skiba edit` opens `$EDITOR` with last response<br>• Save → updates会话 history<br>• Useful for quick tweaks |
| 18 | History Navigation | As a power user, I want to recall previous prompts with arrow keys. | • Prompt history persisted in `~/.skiba/history.jsonl`<br>• Up/Down arrows in interactive mode<br>• `Ctrl+R` fuzzy search like `fzf` |
| 19 | Multi‑Modal Context | As a user, I want to attach images to prompts. | • Support image URLs or local paths in `run`<br>• Encode to base64, send as `image_url`<br>• Auto‑resize/compress if needed |
| 20 | Workspace Profiles | As a developer, I want per‑project config overrides. | • `.skiba.yaml` in cwd overrides global config<br>• Includes model preferences, budgets, allowed skills<br>• Auto‑activate in that directory |

---

### Phase 5: Production & DevOps (Sprints 21-25)
**Goal**: Make it robust, observable, and CI/CD‑ready.

| Sprint | Title | User Stories | Acceptance Criteria |
|--------|-------|--------------|--------------------|
| 21 | Telemetry (Opt‑In) | As a maintainer, I want usage metrics to prioritize fixes. | • Anonymous usage pings (model, tokens, errors)<br>• Opt‑in via `config telemetry on`<br>• Dashboard (or GitHub Actions insights) |
| 22 | Error Reporting | As a user, I want friendly error messages and auto‑reporting (opt‑in). | • Categorize errors (auth, rate‑limit, network, model)<br>• Suggest remedies<br>• `--report` flag sends anonymized stack |
| 23 | Provisioning Scripts | As an operator, I want to install skiba on a fresh machine with one command. | • `make install` / `install.sh` sets up venv, deps, npm link<br>• Checks Python ≥3.8, npm, git<br>• Idempotent |
| 24 | GitHub Action CI | As a contributor, I want CI to run on PRs. | • Lint (ruff), typecheck (mypy), test (pytest)<br>• Coverage reporting to Codecov<br>• Auto‑update deps via Dependabot |
| 25 | Release Automation | As a maintainer, I want one‑click releases to PyPI & npm. | • GitHub Actions: on tag → build & publish<br>• Auto‑generate changelog from conventional commits<br>• Smoke test `npx skiba --version` |

---

### Phase 6: Ecosystem & Growth (Sprints 26-30)
**Goal:** Build a community around skiba.

| Sprint | Title | User Stories | Acceptance Criteria |
|--------|-------|--------------|--------------------|
| 26 | Documentation Site | As a new user, I want a polished docs site to learn quickly. | • MkDocs or Docusaurus site<br>• Quickstart, CLI reference, skill authoring guide<br>• Search, dark theme |
| 27 | Skill Marketplace | As a user, I want to discover useful community skills. | • `skiba skills search <query>` CLI command<br>• Registry on GitHub (skills repo)<br>• Installation via `skiba skills install <name>` |
| 28 | MCP Integration | As an advanced user, I want to connect external tools via Model Context Protocol. | • MCP client built into skiba<br>• Configure servers in `~/.skiba/mcp.json`<br>• Tools from MCP servers appear as skills |
| 29 | Multi‑Model Fallback Chains | As a power user, I want custom fallback strategies per task type. | • Config: `fallback_chain: [claude-sonnet, gemini-flash, minimax]`<br>• Auto‑downgrade on 429/context‑full<br>• Fallback history in receipt |
| 30 | VS Code Extension | As an IDE user, I want skiba inside my editor. | • VS Code extension with `Ctrl+Shift+P` commands<br>• Highlight code → `skiba: explain`<br>• Uses local skiba CLI under the hood |

---

## Handoff Checklist

- [ ] All PRs have linked user stories (Jira/GitHub Issues)
- [ ] Config versioned (`config_version` field) with migrations
- [ ] `handoff.md` updated after each sprint review
- [ ] Core team trained on testing, logging, debugging
- [ ] Published channels: PyPI (`skiba`), npm (`skiba`), GitHub Releases
- [ ] Community health files: CODE_OF_CONDUCT, CONTRIBUTING, SECURITY

---

## Metrics to Track

- **User Adoption**: `npx skiba --version` pings (weekly)
- **Reliability**: 99%+ success rate on API calls (after retries)
- **Cost Efficiency**: Average cost per prompt trending down
- **Skill Usage**: Top executed skills, custom skill installs
- **Session Length**: Avg turns per interactive session

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| API changes from OpenRouter | Weekly sync of model list, strict version pinning per model ID |
| Cost overruns | Budget guardian UI warnings, daily spend caps in config |
| Skill security exploits | Sandboxing (resource limits), skill signing/trust levels |
| Low contribution | Bounty program, good first issue label, dedicated Discord |

---

## Next Steps (Immediate)

1. ~~Prioritize Sprints 1‑3 (Retry, Real Tokens, Tests)~~ ✅ DONE
2. ~~Set up repo: Issues for each user story, project board with 30 columns~~ ✅ Partially done (handoff.md exists)
3. ~~Assign sprint owner(s), define Definition of Done~~ ✅ Done
4. ~~Kickoff Sprint 1~~ ✅ Done
5. **Sprint 4**: Structured Logging (`--debug`/`--json` flags, no API keys in logs)
6. **Sprint 5**: Config Validation (Pydantic schema, `skiba config validate`)
7. Set up GitHub Actions CI (lint, typecheck, test on push)

---

*Document version: 1.0*  
*Maintainer: Skiba Core Team*

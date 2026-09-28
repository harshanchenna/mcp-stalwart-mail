# AGENTS.md

Guide for coding agents (Claude Code, Codex, etc.) and human contributors working in this repo.

## What this is

An MCP (Model Context Protocol) server that sends email over SMTP — two tools, `send_email` and
`send_notification`. Works against any SMTP-capable server (Stalwart, Postfix, Gmail SMTP, etc.),
configured entirely through environment variables. Single-package Python project, no external
services required to develop against (SMTP config is supplied by whoever runs the server).

## How to navigate it

- `src/stalwart_mail_mcp/server.py` — the whole server: tool definitions and SMTP logic.
- `src/stalwart_mail_mcp/__init__.py` — package entry point.
- `pyproject.toml` — dependencies (`mcp[cli]`) and the `stalwart-mail-mcp` console script.
- `README.md` — install/config instructions and the environment variable reference; keep it in
  sync with any new tool or setting.

## Build, test, lint

```bash
uv sync                                          # install deps into .venv
uv run python -c "import stalwart_mail_mcp.server"  # quick import/smoke check
uv run stalwart-mail-mcp                         # run the server (stdio transport)
```

There is no automated test suite or linter configured yet. If you add meaningful logic beyond
straightforward SMTP calls, add `pytest` (as a `dev` optional-dependency group) rather than leaving
it untested.

## Standards this repo owns

- Configuration is environment variables only (see the table in `README.md`) — don't add config
  files or hardcoded defaults that bypass them.
- Keep the server dependency-light; `mcp[cli]` is the only required runtime dependency by design.
- Any new tool must be documented in the `README.md` tools table in the same change.

## PR, review, and commit rules

- Branch → PR → full `/code-review` before merge.
- Merge commits, not squash.
- No `Co-Authored-By` or other AI-attribution lines in commits.
- Secrets (SMTP credentials) live only in `.env` or the consumer's MCP config, never committed —
  this repo ships no `.env` file and none should be added.

Keep this file and the README current when structure or commands change.

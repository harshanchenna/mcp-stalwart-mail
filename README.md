# stalwart-mail-mcp

<!-- mcp-name: io.github.harshanchenna/mcp-stalwart-mail -->

MCP server for sending email via a [Stalwart](https://stalw.art/) mail server using SMTP.

Stalwart is a modern, self-hosted mail server. This MCP server exposes two tools that let Claude Code agents send emails and notifications through any SMTP-capable mail server — including Stalwart, but also standard SMTP relays, Gmail SMTP, etc.

## Quick start

```bash
uvx --from stalwart-mail-mcp stalwart-mail-mcp
```

## Tools

| Tool | Description |
|------|-------------|
| `send_email` | Send an email to one or more recipients with an optional HTML body |
| `send_notification` | Quick notification to a preset address (subject + message only) |

## Configuration

All settings are via environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `SMTP_HOST` | `localhost` | SMTP server hostname |
| `SMTP_PORT` | `25` | SMTP port (25 = relay, 587 = STARTTLS, 465 = SMTPS) |
| `SMTP_FROM` | `agent@example.com` | From address for all outbound mail |
| `SMTP_USERNAME` | *(empty)* | SMTP auth username (leave empty for no-auth relay) |
| `SMTP_PASSWORD` | *(empty)* | SMTP auth password |
| `SMTP_USE_TLS` | `false` | Use implicit TLS/SMTPS (port 465) |
| `SMTP_USE_STARTTLS` | `false` | Use STARTTLS upgrade (port 587) |
| `NOTIFY_TO` | `user@example.com` | Default recipient for `send_notification` |

For an internal Stalwart instance on a trusted network, port 25 relay with no auth is the simplest setup. For external SMTP (e.g. Gmail), use port 587 with `SMTP_USE_STARTTLS=true` and credentials.

## Installation

### Published package with uvx

```bash
# No-auth relay
claude mcp add stalwart-mail \
  -e SMTP_HOST=your-mail-server \
  -e SMTP_PORT=25 \
  -e SMTP_FROM=agent@yourdomain.com \
  -e NOTIFY_TO=you@yourdomain.com \
  -- uvx --from stalwart-mail-mcp stalwart-mail-mcp

# STARTTLS with auth
claude mcp add stalwart-mail \
  -e SMTP_HOST=smtp.gmail.com \
  -e SMTP_PORT=587 \
  -e SMTP_FROM=you@gmail.com \
  -e SMTP_USERNAME=you@gmail.com \
  -e SMTP_PASSWORD=your-app-password \
  -e SMTP_USE_STARTTLS=true \
  -e NOTIFY_TO=you@gmail.com \
  -- uvx --from stalwart-mail-mcp stalwart-mail-mcp
```

```json
{
  "mcpServers": {
    "stalwart-mail": {
      "command": "uvx",
      "args": ["--from", "stalwart-mail-mcp", "stalwart-mail-mcp"],
      "env": {
        "SMTP_HOST": "your-mail-server",
        "SMTP_PORT": "25",
        "SMTP_FROM": "agent@yourdomain.com",
        "NOTIFY_TO": "you@yourdomain.com"
      }
    }
  }
}
```

### From source with uv

```bash
git clone https://github.com/harshanchenna/mcp-stalwart-mail
cd mcp-stalwart-mail

# Add to Claude Code (no-auth relay)
claude mcp add stalwart-mail \
  -e SMTP_HOST=your-mail-server \
  -e SMTP_PORT=25 \
  -e SMTP_FROM=agent@yourdomain.com \
  -e NOTIFY_TO=you@yourdomain.com \
  -- uv run --with-editable . stalwart-mail-mcp

# Add to Claude Code (STARTTLS with auth)
claude mcp add stalwart-mail \
  -e SMTP_HOST=smtp.gmail.com \
  -e SMTP_PORT=587 \
  -e SMTP_FROM=you@gmail.com \
  -e SMTP_USERNAME=you@gmail.com \
  -e SMTP_PASSWORD=your-app-password \
  -e SMTP_USE_STARTTLS=true \
  -e NOTIFY_TO=you@gmail.com \
  -- uv run --with-editable . stalwart-mail-mcp
```

### Manual claude_desktop_config.json entry

```json
{
  "mcpServers": {
    "stalwart-mail": {
      "command": "uv",
      "args": ["run", "--with-editable", "/path/to/mcp-stalwart-mail", "stalwart-mail-mcp"],
      "env": {
        "SMTP_HOST": "your-mail-server",
        "SMTP_PORT": "25",
        "SMTP_FROM": "agent@yourdomain.com",
        "NOTIFY_TO": "you@yourdomain.com"
      }
    }
  }
}
```

## Usage Examples

```python
# Send a formatted report with HTML
send_email(
    to="alice@example.com",
    subject="Daily digest",
    body="All services healthy.",
    html_body="<h2>All services healthy.</h2>"
)

# Send to multiple recipients
send_email(
    to="alice@example.com, bob@example.com",
    subject="Deployment complete",
    body="The v2.1 release is live."
)

# Quick notification from an agent
send_notification(
    subject="Research sprint complete",
    message="Sprint finished. Synthesis doc at docs/2026-04-22_research-topic/_synthesis.md"
)
```

## Requirements

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip
- A running SMTP server (Stalwart, Postfix, or any standard relay)

## License

MIT

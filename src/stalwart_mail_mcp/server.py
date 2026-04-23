"""FastMCP server for sending email via Stalwart mail server (SMTP)."""

from __future__ import annotations

import os
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from mcp.server.fastmcp import FastMCP

# ---------------------------------------------------------------------------
# Configuration (from environment variables)
# ---------------------------------------------------------------------------

SMTP_HOST = os.environ.get("SMTP_HOST", "localhost")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "25"))
SMTP_FROM = os.environ.get("SMTP_FROM", "agent@example.com")
SMTP_USERNAME = os.environ.get("SMTP_USERNAME", "")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")
SMTP_USE_TLS = os.environ.get("SMTP_USE_TLS", "false").lower() in ("true", "1", "yes")
SMTP_USE_STARTTLS = os.environ.get("SMTP_USE_STARTTLS", "false").lower() in ("true", "1", "yes")

# Default notification recipient (for send_notification tool)
NOTIFY_TO = os.environ.get("NOTIFY_TO", "user@example.com")

# ---------------------------------------------------------------------------
# MCP server
# ---------------------------------------------------------------------------

mcp = FastMCP(
    "stalwart-mail",
    instructions=(
        "Send emails via Stalwart mail server. "
        "Use send_email for full control (custom recipients, HTML body). "
        "Use send_notification for quick messages to the default address."
    ),
)


# ---------------------------------------------------------------------------
# Internal SMTP helper
# ---------------------------------------------------------------------------

def _send_via_smtp(
    to: list[str],
    subject: str,
    body: str,
    html_body: str | None = None,
    from_addr: str | None = None,
) -> None:
    """Send an email via SMTP. Raises on failure."""
    sender = from_addr or SMTP_FROM

    if html_body:
        msg: MIMEMultipart | MIMEText = MIMEMultipart("alternative")
        msg.attach(MIMEText(body, "plain"))
        msg.attach(MIMEText(html_body, "html"))
    else:
        msg = MIMEText(body, "plain")

    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = ", ".join(to)

    if SMTP_USE_TLS:
        # SMTPS (implicit TLS, typically port 465)
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=context) as smtp:
            if SMTP_USERNAME:
                smtp.login(SMTP_USERNAME, SMTP_PASSWORD)
            smtp.sendmail(sender, to, msg.as_string())
    else:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
            if SMTP_USE_STARTTLS:
                smtp.starttls()
            if SMTP_USERNAME:
                smtp.login(SMTP_USERNAME, SMTP_PASSWORD)
            smtp.sendmail(sender, to, msg.as_string())


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------

@mcp.tool()
def send_email(
    to: str,
    subject: str,
    body: str,
    html_body: str | None = None,
    cc: str | None = None,
) -> str:
    """Send an email to one or more recipients.

    Args:
        to: Recipient email address(es), comma-separated.
            Examples: "alice@example.com" or "alice@example.com, bob@example.com"
        subject: Email subject line.
        body: Plain-text email body.
        html_body: Optional HTML version of the body. When provided, email clients
                   that support HTML will render it; others fall back to plain text.
        cc: Optional CC recipient(s), comma-separated.
    """
    to_list = [addr.strip() for addr in to.split(",") if addr.strip()]
    if not to_list:
        return "Error: no valid recipients provided."

    try:
        _send_via_smtp(
            to=to_list,
            subject=subject,
            body=body,
            html_body=html_body,
        )
    except Exception as exc:
        return f"Error sending email: {exc}"

    recipients_str = ", ".join(to_list)
    return f"Email sent successfully to {recipients_str} | Subject: {subject!r}"


@mcp.tool()
def send_notification(subject: str, message: str) -> str:
    """Send a quick notification email to the default address (NOTIFY_TO env var).

    This is a convenience wrapper around send_email for agent notifications,
    reports, and summaries that always go to the same recipient.

    Args:
        subject: Notification subject line.
        message: Notification body text.
    """
    try:
        _send_via_smtp(
            to=[NOTIFY_TO],
            subject=subject,
            body=message,
        )
    except Exception as exc:
        return f"Error sending notification: {exc}"

    return f"Notification sent to {NOTIFY_TO} | Subject: {subject!r}"


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()

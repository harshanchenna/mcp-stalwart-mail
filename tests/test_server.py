"""Smoke tests: the server imports, exposes its tools, and validates input
without opening any real SMTP connection or requiring credentials."""

from __future__ import annotations

import asyncio

from stalwart_mail_mcp import server

EXPECTED_TOOLS = {"send_email", "send_notification"}


def test_all_tools_are_registered() -> None:
    tools = asyncio.run(server.mcp.list_tools())
    names = {t.name for t in tools}
    assert EXPECTED_TOOLS <= names


def test_send_email_rejects_empty_recipient_list() -> None:
    result = server.send_email(to="   , ,", subject="hi", body="body")
    assert "no valid recipients" in result.lower()


def test_send_email_success_path(monkeypatch) -> None:
    sent: dict = {}

    class _FakeSMTP:
        def __init__(self, host, port):
            sent["host"] = host
            sent["port"] = port

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

        def sendmail(self, sender, to, msg):
            sent["sender"] = sender
            sent["to"] = to
            sent["msg"] = msg

    monkeypatch.setattr(server.smtplib, "SMTP", _FakeSMTP)

    result = server.send_email(to="alice@example.com", subject="Subject", body="Body text")

    assert "sent successfully" in result.lower()
    assert sent["to"] == ["alice@example.com"]
    assert sent["sender"] == server.SMTP_FROM


def test_send_email_reports_smtp_failure(monkeypatch) -> None:
    class _FailingSMTP:
        def __init__(self, *a, **k):
            raise ConnectionRefusedError("no mail server here")

    monkeypatch.setattr(server.smtplib, "SMTP", _FailingSMTP)

    result = server.send_email(to="alice@example.com", subject="Subject", body="Body")
    assert result.startswith("Error sending email:")


def test_send_notification_uses_default_recipient(monkeypatch) -> None:
    sent: dict = {}

    class _FakeSMTP:
        def __init__(self, host, port):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

        def sendmail(self, sender, to, msg):
            sent["to"] = to

    monkeypatch.setattr(server.smtplib, "SMTP", _FakeSMTP)

    result = server.send_notification(subject="Heads up", message="all good")
    assert sent["to"] == [server.NOTIFY_TO]
    assert "sent to" in result.lower()


def test_main_entry_point_exists() -> None:
    assert callable(server.main)

#!/usr/bin/env python3
"""IMAP/SMTP helper for william@florinmanagement.com (Hostinger email).

Credentials live in ~/.florin-mail.env (never in this repo).

Usage:
  mail.py probe                          -> test IMAP + SMTP logins (read-only)
  mail.py read [N]                       -> list the N most recent inbox messages (default 5)
  mail.py send <to> <subject> <body...>  -> send a plain-text email
"""

import email
import email.header
import imaplib
import os
import smtplib
import sys
from email.message import EmailMessage
from pathlib import Path

ENV_FILE = Path.home() / ".florin-mail.env"


def load_env() -> dict:
    cfg = {}
    for line in ENV_FILE.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            cfg[k] = v
    missing = [k for k in ("FLORIN_EMAIL", "FLORIN_EMAIL_PASSWORD") if not cfg.get(k)]
    if missing:
        sys.exit(f"Missing in {ENV_FILE}: {', '.join(missing)}")
    return cfg


def imap_connect(cfg) -> imaplib.IMAP4_SSL:
    conn = imaplib.IMAP4_SSL(cfg["FLORIN_IMAP_HOST"], int(cfg.get("FLORIN_IMAP_PORT", 993)))
    conn.login(cfg["FLORIN_EMAIL"], cfg["FLORIN_EMAIL_PASSWORD"])
    return conn


def decode(value: str) -> str:
    parts = email.header.decode_header(value or "")
    return "".join(p.decode(enc or "utf-8", "replace") if isinstance(p, bytes) else p for p, enc in parts)


def cmd_probe(cfg) -> None:
    conn = imap_connect(cfg)
    _, data = conn.select("INBOX", readonly=True)
    print(f"IMAP OK — INBOX has {data[0].decode()} message(s)")
    conn.logout()

    with smtplib.SMTP_SSL(cfg["FLORIN_SMTP_HOST"], int(cfg.get("FLORIN_SMTP_PORT", 465))) as smtp:
        smtp.login(cfg["FLORIN_EMAIL"], cfg["FLORIN_EMAIL_PASSWORD"])
    print("SMTP OK — login accepted")


def cmd_read(cfg, count: int) -> None:
    conn = imap_connect(cfg)
    conn.select("INBOX", readonly=True)
    _, data = conn.search(None, "ALL")
    ids = data[0].split()
    if not ids:
        print("INBOX is empty.")
    for msg_id in reversed(ids[-count:]):
        _, msg_data = conn.fetch(msg_id, "(BODY.PEEK[HEADER.FIELDS (FROM TO SUBJECT DATE)])")
        hdr = email.message_from_bytes(msg_data[0][1])
        print(f"#{msg_id.decode()}  {decode(hdr['Date'])}")
        print(f"    From: {decode(hdr['From'])}   To: {decode(hdr['To'])}")
        print(f"    Subject: {decode(hdr['Subject'])}")
    conn.logout()


def cmd_send(cfg, to: str, subject: str, body: str) -> None:
    msg = EmailMessage()
    msg["From"] = cfg["FLORIN_EMAIL"]
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(body)
    with smtplib.SMTP_SSL(cfg["FLORIN_SMTP_HOST"], int(cfg.get("FLORIN_SMTP_PORT", 465))) as smtp:
        smtp.login(cfg["FLORIN_EMAIL"], cfg["FLORIN_EMAIL_PASSWORD"])
        smtp.send_message(msg)
    print(f"Sent to {to}: {subject}")


def main() -> None:
    cfg = load_env()
    cmd = sys.argv[1] if len(sys.argv) > 1 else "probe"
    if cmd == "probe":
        cmd_probe(cfg)
    elif cmd == "read":
        cmd_read(cfg, int(sys.argv[2]) if len(sys.argv) > 2 else 5)
    elif cmd == "send":
        if len(sys.argv) < 5:
            sys.exit("usage: mail.py send <to> <subject> <body...>")
        cmd_send(cfg, sys.argv[2], sys.argv[3], " ".join(sys.argv[4:]))
    else:
        sys.exit(f"unknown command: {cmd}")


if __name__ == "__main__":
    main()

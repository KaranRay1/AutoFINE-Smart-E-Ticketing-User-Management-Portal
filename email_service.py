"""
Email service for AutoFINE (SMTP-based).

To enable emailing reports, set environment variables:
- SMTP_HOST (e.g. smtp.gmail.com)
- SMTP_PORT (e.g. 587)
- SMTP_USER (sender email)
- SMTP_PASS (app password / smtp password)
- REPORT_TO_EMAIL (default receiver; optional)
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_email(to_email: str, subject: str, body: str) -> None:
    host = os.environ.get("SMTP_HOST")
    port = int(os.environ.get("SMTP_PORT", "587"))
    user = os.environ.get("SMTP_USER")
    pwd = os.environ.get("SMTP_PASS")

    if not host or not user or not pwd:
        raise RuntimeError("Email not configured (set SMTP_HOST/SMTP_USER/SMTP_PASS).")

    msg = MIMEMultipart()
    msg["From"] = user
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain", "utf-8"))

    with smtplib.SMTP(host, port, timeout=20) as server:
        server.starttls()
        server.login(user, pwd)
        server.sendmail(user, [to_email], msg.as_string())


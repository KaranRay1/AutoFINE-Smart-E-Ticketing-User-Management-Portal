"""
Simple SMS notification stub for challan updates.
This is a mock that logs SMS messages; replace with real gateway (e.g., Twilio) in production.
"""

import datetime


def send_sms(phone_number: str, message: str) -> bool:
    """Mock SMS sender; logs to console and returns True."""
    if not phone_number:
        return False
    timestamp = datetime.datetime.now().isoformat()
    print(f"[SMS {timestamp}] To: {phone_number} | {message}")
    return True

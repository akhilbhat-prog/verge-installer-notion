import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from email_fetch import fetch_emails


def test_latest_email():
    emails = fetch_emails(latest=True)

    assert emails, "No emails returned"

    msg, meta = emails[0]

    assert meta.message_id
    assert meta.subject is not None
    assert meta.sender is not None
    assert meta.received_at.tzinfo is not None
    assert meta.html_path.endswith(".html")

    print("✅ Email fetch OK")
    print("Subject:", meta.subject)
    print("From:", meta.sender)
    print("Received:", meta.received_at)


if __name__ == "__main__":
    test_latest_email()

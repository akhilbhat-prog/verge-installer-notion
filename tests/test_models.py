import sys
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from models import EmailMeta


def test_email_meta():
    dt = datetime.now(timezone.utc)

    meta = EmailMeta(
        message_id="abc123",
        subject="Test Subject",
        sender="test@example.com",
        received_at=dt,
        folder="INBOX",
        html_path="artifacts/emails/abc123.html",
    )

    assert meta.message_id == "abc123"
    assert meta.received_at.tzinfo is not None

    print("✅ EmailMeta model works correctly")


if __name__ == "__main__":
    test_email_meta()

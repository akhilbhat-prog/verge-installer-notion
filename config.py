import os
import sys
from pathlib import Path
from datetime import timezone, timedelta
from dotenv import load_dotenv

# Ensure project root is on sys.path for absolute imports from any entry point
_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

load_dotenv()

YAHOO_EMAIL = os.getenv("YAHOO_EMAIL")
YAHOO_APP_PASSWORD = os.getenv("YAHOO_APP_PASSWORD")
NEWSLETTER_FROM = os.getenv("NEWSLETTER_FROM", "")

IMAP_HOST = "imap.mail.yahoo.com"
IMAP_PORT = 993
DEFAULT_FOLDER = os.getenv("YAHOO_IMAP_FOLDER", "INBOX")

IST = timezone(timedelta(hours=5, minutes=30), name="IST")

ARTIFACTS_DIR = Path("artifacts")
EMAIL_DIR = ARTIFACTS_DIR / "emails"
PARSED_DIR = ARTIFACTS_DIR / "parsed"
RENDERED_DIR = ARTIFACTS_DIR / "rendered"


def ensure_artifact_dirs() -> None:
    for d in (EMAIL_DIR, PARSED_DIR, RENDERED_DIR):
        d.mkdir(parents=True, exist_ok=True)


if not YAHOO_EMAIL or not YAHOO_APP_PASSWORD:
    raise RuntimeError("Missing Yahoo IMAP credentials")

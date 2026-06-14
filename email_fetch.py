import imaplib
import json
import logging
from email import message_from_bytes
from email.header import decode_header
from email.utils import parsedate_to_datetime
from datetime import datetime, timedelta

from config import (
    IMAP_HOST,
    IMAP_PORT,
    YAHOO_EMAIL,
    YAHOO_APP_PASSWORD,
    DEFAULT_FOLDER,
    NEWSLETTER_FROM,
    IST,
    EMAIL_DIR,
)
from models import EmailMeta

log = logging.getLogger("email_fetch")


def _decode(value: str | None) -> str:
    if not value:
        return ""
    parts = decode_header(value)
    return "".join(
        part.decode(enc or "utf-8", errors="replace")
        if isinstance(part, bytes)
        else part
        for part, enc in parts
    )


def fetch_emails(
    *,
    folder: str = DEFAULT_FOLDER,
    latest: bool = False,
    last_n: int | None = None,
    days: int | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
):
    """
    Fetch emails from Yahoo IMAP and return (email.message.Message, EmailMeta) tuples.
    Deduplicates based on Message-ID metadata JSON existing on disk.
    """

    mail = imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT)
    mail.login(YAHOO_EMAIL, YAHOO_APP_PASSWORD)
    try:
        mail.select(folder, readonly=True)

        # --- Select message IDs ---
        if latest:
            if NEWSLETTER_FROM:
                search_criteria = f'FROM "{NEWSLETTER_FROM}"'
                log.info("Searching for emails from %s", NEWSLETTER_FROM)
            else:
                search_criteria = "ALL"
                log.warning("NEWSLETTER_FROM not set; searching all emails (may miss newsletter)")

            # Search configured folder + INBOX so we find emails not yet moved by rules
            folders_to_search = [folder]
            if folder.upper() != "INBOX":
                folders_to_search.append("INBOX")

            best_id, best_date, best_folder = None, None, folder
            for sf in folders_to_search:
                mail.select(sf, readonly=True)
                _, data = mail.search(None, search_criteria)
                log.info("Folder %s: %d match(es)", sf, len(data[0].split()))
                for cid in data[0].split():
                    _, hdata = mail.fetch(cid, "(BODY.PEEK[HEADER.FIELDS (DATE)])")
                    raw = hdata[0][1].decode(errors="replace")
                    date_line = next(
                        (l for l in raw.splitlines() if l.lower().startswith("date:")), None
                    )
                    if date_line:
                        try:
                            dt = parsedate_to_datetime(date_line[5:].strip())
                            if best_date is None or dt > best_date:
                                best_date, best_id, best_folder = dt, cid, sf
                        except Exception:
                            pass

            if best_id is not None:
                mail.select(best_folder, readonly=True)
                folder = best_folder  # fetch below must be in this folder
                ids = [best_id]
                log.info("Latest newsletter found in folder: %s", best_folder)
            else:
                log.warning("No emails found matching search criteria in any folder")
                ids = []
        elif last_n:
            _, data = mail.search(None, "ALL")
            ids = data[0].split()[-last_n:]
        elif days:
            since = (datetime.now(IST) - timedelta(days=days)).strftime("%d-%b-%Y")
            _, data = mail.search(None, f"SINCE {since}")
            ids = data[0].split()
        elif date_from and date_to:
            since = date_from.strftime("%d-%b-%Y")
            before = (date_to + timedelta(days=1)).strftime("%d-%b-%Y")
            _, data = mail.search(None, f"SINCE {since} BEFORE {before}")
            ids = data[0].split()
        else:
            raise ValueError("No valid email selection mode specified")

        results: list[tuple] = []

        for msg_id in ids:
            _, data = mail.fetch(msg_id, "(BODY.PEEK[])")
            msg = message_from_bytes(data[0][1])

            message_id = (msg.get("Message-ID") or "").strip("<>")
            if not message_id:
                log.warning("Skipping email without Message-ID")
                continue

            meta_path = EMAIL_DIR / f"{message_id}.json"
            html_path = EMAIL_DIR / f"{message_id}.html"

            # Deduplication
            if meta_path.exists():
                log.info("Skipping duplicate email %s", message_id)
                continue

            # Parse date
            received_at = parsedate_to_datetime(msg.get("Date"))
            if received_at.tzinfo is None:
                received_at = received_at.replace(tzinfo=IST)
            received_at = received_at.astimezone(IST)

            meta = EmailMeta(
                message_id=message_id,
                subject=_decode(msg.get("Subject")),
                sender=_decode(msg.get("From")),
                received_at=received_at,
                folder=folder,
                html_path=str(html_path),
            )

            meta_path.write_text(
                json.dumps(
                    {
                        "message_id": meta.message_id,
                        "subject": meta.subject,
                        "sender": meta.sender,
                        "received_at": meta.received_at.isoformat(),
                        "folder": meta.folder,
                        "html_path": meta.html_path,
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )

            results.append((msg, meta))
            log.info("Fetched email: %s", meta.subject)

    finally:
        mail.logout()

    return results

import logging
from email.message import Message

log = logging.getLogger("html_extract")


def extract_html(msg: Message) -> str:
    if msg.is_multipart():
        html = None
        text = None

        for part in msg.walk():
            if part.get_content_type() == "text/html":
                html = part
            elif part.get_content_type() == "text/plain":
                text = part

        if html:
            payload = html.get_payload(decode=True)
            return payload.decode(html.get_content_charset() or "utf-8", errors="replace")

        if text:
            payload = text.get_payload(decode=True)
            content = payload.decode(text.get_content_charset() or "utf-8", errors="replace")
            return f"<html><body><pre>{content}</pre></body></html>"

        return ""

    payload = msg.get_payload(decode=True)
    return payload.decode(msg.get_content_charset() or "utf-8", errors="replace")

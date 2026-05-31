from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class EmailMeta:
    message_id: str
    subject: str
    sender: str
    received_at: datetime
    folder: str
    html_path: str

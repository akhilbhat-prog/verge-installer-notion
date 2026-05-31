import os
from dotenv import load_dotenv

load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")
NOTION_TITLE_PROPERTY = os.getenv("NOTION_TITLE_PROPERTY")
NOTION_DATE_PROPERTY = os.getenv("NOTION_DATE_PROPERTY")

if not all(
    [
        NOTION_TOKEN,
        NOTION_DATABASE_ID,
        NOTION_TITLE_PROPERTY,
        NOTION_DATE_PROPERTY,
    ]
):
    raise RuntimeError("Missing required Notion environment variables")

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
}

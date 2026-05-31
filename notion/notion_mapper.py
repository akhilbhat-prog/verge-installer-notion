from datetime import datetime
from typing import List

from notion.notion_config import (
    NOTION_DATABASE_ID,
    NOTION_TITLE_PROPERTY,
    NOTION_DATE_PROPERTY,
)


def build_page_payload(*, title: str, date_iso: str) -> dict:
    """
    Build the Notion page payload.
    Stores DATE ONLY (YYYY-MM-DD) in the Notion date property.
    """
    # Convert ISO datetime → date-only string
    date_only = datetime.fromisoformat(date_iso).date().isoformat()

    return {
        "parent": {"database_id": NOTION_DATABASE_ID},
        "properties": {
            NOTION_TITLE_PROPERTY: {
                "title": [{"text": {"content": title}}]
            },
            NOTION_DATE_PROPERTY: {
                "date": {"start": date_only}
            },
        },
    }


def heading_block(text: str) -> dict:
    return {
        "object": "block",
        "type": "heading_2",
        "heading_2": {
            "rich_text": [{"type": "text", "text": {"content": text}}],
        },
    }


def paragraph_block(text: str) -> dict:
    return {
        "object": "block",
        "type": "paragraph",
        "paragraph": {
            "rich_text": [{"type": "text", "text": {"content": text}}],
        },
    }


def bullet_link_block(label: str, url: str) -> dict:
    return {
        "object": "block",
        "type": "bulleted_list_item",
        "bulleted_list_item": {
            "rich_text": [
                {
                    "type": "text",
                    "text": {
                        "content": label,
                        "link": {"url": url},
                    },
                }
            ]
        },
    }


def parsed_to_blocks(parsed_sections: list[dict]) -> List[dict]:
    blocks: List[dict] = []

    for section in parsed_sections:
        blocks.append(heading_block(section["title"]))

        for sub in section["subsections"]:
            if sub["text"]:
                blocks.append(paragraph_block(sub["text"]))

            for link in sub["links"]:
                blocks.append(bullet_link_block(link["label"], link["url"]))

    return blocks

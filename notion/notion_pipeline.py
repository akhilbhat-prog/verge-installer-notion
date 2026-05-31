import config  # noqa: F401 — triggers sys.path setup via config.py
import argparse
import json
import logging
from datetime import datetime

from config import PARSED_DIR, EMAIL_DIR
from notion.notion_client import post, patch
from notion.notion_mapper import build_page_payload, parsed_to_blocks

log = logging.getLogger("notion_pipeline")


def load_parsed(message_id: str) -> list[dict]:
    path = PARSED_DIR / f"{message_id}.json"
    if not path.exists():
        raise FileNotFoundError(f"Parsed file not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def load_email_meta(message_id: str) -> dict:
    path = EMAIL_DIR / f"{message_id}.json"
    if not path.exists():
        raise FileNotFoundError(f"Email meta not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def build_title(date_iso: str) -> str:
    dt = datetime.fromisoformat(date_iso)
    return f"Installer-{dt.strftime('%B-%d-%Y')}"


def preview(message_id: str):
    meta = load_email_meta(message_id)
    parsed = load_parsed(message_id)

    title = build_title(meta["received_at"])
    blocks = parsed_to_blocks(parsed)

    print("\n=== NOTION PREVIEW ===\n")
    print("Title:", title)
    print("Date:", meta["received_at"])
    print("\nBlocks:\n")

    for block in blocks:
        block_type = block["type"]

        if block_type.startswith("heading"):
            rich_text = block[block_type].get("rich_text", [])
            text = rich_text[0]["text"]["content"] if rich_text else ""
            print(f"[H] {text}")

        elif block_type == "paragraph":
            rich_text = block["paragraph"].get("rich_text", [])
            text = rich_text[0]["text"]["content"] if rich_text else ""
            print(f"[P] {text}")

        elif block_type == "bulleted_list_item":
            rich_text = block["bulleted_list_item"].get("rich_text", [])
            if rich_text:
                rt = rich_text[0]["text"]
                label = rt["content"]
                url = rt.get("link", {}).get("url", "")
                print(f"[•] {label} -> {url}")

    print("\n=== END PREVIEW ===\n")


def push(message_id: str):
    meta = load_email_meta(message_id)
    parsed = load_parsed(message_id)

    title = build_title(meta["received_at"])
    blocks = parsed_to_blocks(parsed)

    # 1️⃣ Create the page
    page = post(
        "https://api.notion.com/v1/pages",
        build_page_payload(
            title=title,
            date_iso=meta["received_at"],
        ),
    )

    page_id = page["id"]
    log.info("Created Notion page %s", page_id)

    # 2️⃣ Append blocks in chunks of 100 (PATCH, not POST)
    for i in range(0, len(blocks), 100):
        chunk = blocks[i : i + 100]
        patch(
            f"https://api.notion.com/v1/blocks/{page_id}/children",
            {"children": chunk},
        )

    print("✅ Page created:", page["url"])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["preview", "push"])
    parser.add_argument("message_id")
    args = parser.parse_args()

    if args.command == "preview":
        preview(args.message_id)
    else:
        push(args.message_id)


if __name__ == "__main__":
    main()

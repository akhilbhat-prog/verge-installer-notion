import argparse
import logging
from pathlib import Path

from config import ensure_artifact_dirs
from logging_setup import setup_logging
from email_fetch import fetch_emails
from html_extract import extract_html
from parse_pipeline import parse_html_file
from notion.notion_pipeline import preview as notion_preview
from notion.notion_pipeline import push as notion_push


log = logging.getLogger("run_all")


def run(latest: bool, mode: str):
    ensure_artifact_dirs()
    setup_logging()
    log.info("Starting end-to-end pipeline: mode=%s", mode)

    # 1. Fetch email(s)
    emails = fetch_emails(latest=latest)
    if not emails:
        log.warning("No emails fetched. Exiting.")
        return

    msg, meta = emails[0]
    message_id = meta.message_id
    log.info("Processing email: %s", meta.subject)

    # 2. Extract HTML
    html = extract_html(msg)
    html_path = Path(meta.html_path)
    html_path.write_text(html, encoding="utf-8")
    log.info("HTML written to %s", html_path)

    # 3. Parse + clean + render
    parsed_path, rendered_path = parse_html_file(html_path)
    log.info("Parsed content written to %s", parsed_path)
    log.info("Rendered preview written to %s", rendered_path)

    # 4. Notion step
    if mode == "preview":
        notion_preview(message_id)
    elif mode == "push":
        notion_push(message_id)
    else:
        raise ValueError(f"Unknown mode: {mode}")

    log.info("Pipeline completed successfully")


def main():
    parser = argparse.ArgumentParser(description="Run full Yahoo → Notion pipeline")
    parser.add_argument(
        "--latest",
        action="store_true",
        default=True,
        help="Process latest email (default and only supported mode)",
    )
    parser.add_argument(
        "--mode",
        choices=["preview", "push"],
        required=True,
        help="Preview or push to Notion",
    )

    args = parser.parse_args()
    run(latest=args.latest, mode=args.mode)


if __name__ == "__main__":
    main()

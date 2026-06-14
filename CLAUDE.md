# Verge Installer → Notion Pipeline

Fetches "The Installer" newsletter (The Verge) from a Yahoo Mail inbox via IMAP,
parses the HTML into structured sections, and pushes a formatted page to a Notion database.

## How to run locally

```powershell
.venv\Scripts\activate
python run_all.py --mode push --latest    # fetch + parse + push to Notion
python run_all.py --mode preview --latest # fetch + parse + print dry-run (no Notion write)
```

## Key files

| File | Purpose |
|------|---------|
| `run_all.py` | Main entry point — orchestrates all 4 pipeline steps |
| `config.py` | Loads `.env`, defines all path constants, adds root to sys.path |
| `email_fetch.py` | Yahoo IMAP fetch; picks most-recent email by Date header across last 10 messages |
| `html_extract.py` | Extracts HTML body from raw email message |
| `section_parser.py` | BeautifulSoup parser — splits into known sections (The Drop, Screen Share, etc.) |
| `parse_pipeline.py` | Orchestrates parse → clean → render → write JSON + TXT to artifacts/ |
| `text_cleanup.py` | Removes boilerplate paragraphs (legal, CTAs, unsubscribe) |
| `preview_renderer.py` | Renders parsed sections as plain text |
| `notion/notion_pipeline.py` | preview() and push(); checks for duplicate Notion page before creating |
| `notion/notion_client.py` | Thin requests wrapper: post(), patch(), query() |
| `notion/notion_mapper.py` | Converts parsed section dicts → Notion block dicts |

## Credentials

- **Local:** `.env` file in project root (never committed — in `.gitignore`)
- **CI:** GitHub Secrets on `akhilbhat-prog/verge-installer-notion`

Required env vars: `YAHOO_EMAIL`, `YAHOO_APP_PASSWORD`, `YAHOO_IMAP_FOLDER`,
`NEWSLETTER_FROM`, `NOTION_TOKEN`, `NOTION_DATABASE_ID`, `NOTION_TITLE_PROPERTY`,
`NOTION_DATE_PROPERTY`

## Automation

GitHub Actions workflow: `.github/workflows/run_installer.yml`
- Runs `python run_all.py --mode push --latest`
- Scheduled: **Friday, Saturday, Sunday at 13:00 UTC (6:30pm IST)**
- Also triggerable manually via `workflow_dispatch`

## Deduplication

Two layers:
1. **IMAP:** skips emails whose `{message_id}.json` already exists in `artifacts/emails/`
   (works locally; `artifacts/` is ephemeral in CI so this layer doesn't apply there)
2. **Notion:** `page_exists()` queries the database for a page with the same title before
   creating — this is the primary dedup layer in CI and prevents duplicate pages on
   Fri/Sat/Sun runs

## Artifacts

`artifacts/` is gitignored and created at runtime:
- `artifacts/emails/` — raw HTML + metadata JSON per email
- `artifacts/parsed/` — structured JSON per email
- `artifacts/rendered/` — plain-text preview per email

## Archive

`_archive/` is gitignored and holds legacy files (pipeline.py, debug scripts, etc.)

# Project Handoff: VergeInstaller → GitHub + Zapier + Notion

## What this project does

Fetches "The Installer" newsletter (from The Verge) from a Yahoo Mail inbox via IMAP,
parses the HTML into structured sections, and pushes a formatted page to a Notion database.
Currently run manually every weekend. Goal: make it fully automatic — email arrives → Notion
page created, with no PC intervention required.

---

## Current codebase structure

```
VergeInstallerYahoo2026/
├── .env                        # ⚠️ Contains real credentials — must NOT be committed
├── config.py                   # Reads .env, sets constants
├── models.py                   # EmailMeta dataclass
├── logging_setup.py
├── email_fetch.py              # Yahoo IMAP fetch (deduplication built in)
├── html_extract.py             # Pulls HTML body from email message
├── section_parser.py           # BeautifulSoup parser — splits into known sections
├── parser_models.py            # Section / Subsection / Link dataclasses
├── parse_pipeline.py           # Orchestrates parse → JSON + rendered TXT
├── preview_renderer.py         # Renders parsed sections as plain text
├── text_cleanup.py             # Filters boilerplate paragraphs
├── run_all.py                  # ⭐ Main entry point: --mode preview|push
├── pipeline.py                 # Older entry point (fetch + extract only)
├── notion/
│   ├── notion_client.py        # Thin wrapper around Notion REST API
│   ├── notion_config.py        # Reads Notion env vars
│   ├── notion_mapper.py        # Converts parsed sections → Notion block dicts
│   └── notion_pipeline.py      # preview() and push() functions
├── tests/
│   └── test_parse_pipeline.py  # Runs parse pipeline + asserts output quality
└── artifacts/                  # Runtime output — emails/, parsed/, rendered/
```

The full pipeline (run via `python run_all.py --mode push --latest`) does:
1. Connect to Yahoo IMAP → fetch latest email from `Inbox/Installer`
2. Extract HTML body → save to `artifacts/emails/<message-id>.html`
3. Parse HTML into sections/subsections/links → `artifacts/parsed/<message-id>.json`
4. Render plain-text preview → `artifacts/rendered/<message-id>.txt`
5. POST to Notion API → creates a page titled `Installer-{Month-DD-YYYY}`

---

## .env contents (values to move to GitHub Secrets)

```
YAHOO_EMAIL=akhilbhat88@yahoo.in
YAHOO_APP_PASSWORD=<yahoo app password>
YAHOO_IMAP_FOLDER=Inbox/Installer
NEWSLETTER_FROM=installer@theverge.com
NOTION_TOKEN=<notion integration token>
NOTION_DATABASE_ID=2659ed42-dd5a-8062-8552-f09282a26b4a
NOTION_TITLE_PROPERTY=Name
NOTION_DATE_PROPERTY=Date
```

All of these must be added as GitHub repository secrets (repo Settings → Secrets and variables
→ Actions). The workflow will inject them as environment variables.

---

## Target architecture

```
Yahoo inbox receives Installer email
        ↓
   Zapier watches inbox (filter: from = installer@theverge.com)
        ↓
   Zapier calls GitHub Actions workflow_dispatch webhook
        ↓
   GitHub Actions runner:
     - checks out repo
     - installs Python deps (pip install -r requirements.txt)
     - runs: python run_all.py --mode push --latest
        ↓
   Notion page created ✅
```

---

## What needs to be built

### 1. `.gitignore`
Must exclude at minimum:
- `.env`
- `.venv/`
- `artifacts/`
- `__pycache__/`
- `*.pyc`
- `.idea/`

### 2. `requirements.txt`
Does not currently exist. Needs to be generated from the venv.
Key packages: `beautifulsoup4`, `python-dotenv`, `requests` (or `httpx`).
Check `notion/notion_client.py` to confirm which HTTP library is used.

### 3. `.github/workflows/run_installer.yml`
A GitHub Actions workflow triggered by `workflow_dispatch` (so Zapier can call it via the
GitHub API). Should:
- Run on `ubuntu-latest`
- Use Python 3.13 (matches local venv)
- `pip install -r requirements.txt`
- Run `python run_all.py --mode push --latest`
- Pass all secrets from GitHub Secrets as environment variables

### 4. GitHub repo setup
- Repo name suggestion: `verge-installer-notion` (or keep `VergeInstallerYahoo2026`)
- Visibility: Public
- After pushing, add all secrets from the `.env` file under repo Settings → Secrets

### 5. Zapier setup (do last, after workflow is confirmed working)
- Trigger: "New Email" in Yahoo Mail, filtered to `From contains installer@theverge.com`
- Action: "Trigger a GitHub Actions Workflow Run" (or use a Webhooks POST action to
  `https://api.github.com/repos/{owner}/{repo}/actions/workflows/run_installer.yml/dispatches`)
  with a Bearer token (GitHub Personal Access Token with `repo` + `workflow` scopes)

---

## Key things to verify before Zapier setup

1. The workflow runs successfully end-to-end via manual `workflow_dispatch` trigger in
   the GitHub Actions UI (with secrets set)
2. The `artifacts/` directory is created at runtime by the pipeline — this is fine on
   GitHub Actions since it only needs to exist during the run
3. Deduplication in `email_fetch.py` is based on `artifacts/emails/<id>.json` existing —
   this won't persist between GitHub Actions runs, but that's OK since each run starts
   fresh and processes only the latest email

---

## Notes

- The `.env` file should NOT be deleted locally — just ensure it's in `.gitignore`
- `WorkingCodeCommit.rar` and `legacy/` folder can be excluded from the repo or kept —
  they appear to be backups
- The `tests/test_parse_pipeline.py` can optionally be added as a workflow step before push
  to act as a quality gate

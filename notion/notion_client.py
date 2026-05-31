import requests
import logging

from notion.notion_config import HEADERS

log = logging.getLogger("notion_client")


def post(url: str, payload: dict) -> dict:
    resp = requests.post(url, headers=HEADERS, json=payload)
    if not resp.ok:
        raise RuntimeError(f"Notion API error {resp.status_code}: {resp.text}")
    return resp.json()


def patch(url: str, payload: dict) -> dict:
    resp = requests.patch(url, headers=HEADERS, json=payload)
    if not resp.ok:
        raise RuntimeError(f"Notion API error {resp.status_code}: {resp.text}")
    return resp.json()


def query(url: str, payload: dict) -> dict:
    resp = requests.post(url, headers=HEADERS, json=payload)
    if not resp.ok:
        raise RuntimeError(f"Notion API error {resp.status_code}: {resp.text}")
    return resp.json()

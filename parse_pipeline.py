import json
import logging
from pathlib import Path

from config import PARSED_DIR, RENDERED_DIR
from section_parser import parse_html
from preview_renderer import render_sections
from text_cleanup import should_remove_paragraph
from parser_models import Section

log = logging.getLogger("parse_pipeline")


def _serialize_sections(sections: list[Section]) -> list[dict]:
    out = []
    for section in sections:
        out.append(
            {
                "title": section.title,
                "subsections": [
                    {
                        "text": sub.text,
                        "links": [
                            {"label": link.label, "url": link.url}
                            for link in sub.links
                        ],
                    }
                    for sub in section.subsections
                ],
            }
        )
    return out


def parse_html_file(html_path: Path):
    html = html_path.read_text(encoding="utf-8")
    sections = parse_html(html)

    cleaned_sections: list[Section] = []
    for section in sections:
        kept_subsections = [
            sub for sub in section.subsections
            if not should_remove_paragraph(sub.text)
        ]
        if not kept_subsections:
            continue
        section.subsections = kept_subsections
        cleaned_sections.append(section)

    rendered = render_sections(cleaned_sections)

    base = html_path.stem
    parsed_path = PARSED_DIR / f"{base}.json"
    rendered_path = RENDERED_DIR / f"{base}.txt"

    parsed_path.write_text(
        json.dumps(_serialize_sections(cleaned_sections), indent=2),
        encoding="utf-8",
    )
    rendered_path.write_text(rendered, encoding="utf-8")

    log.info("Parsed HTML → %s", parsed_path.name)
    log.info("Rendered preview → %s", rendered_path.name)

    return parsed_path, rendered_path

import logging
from bs4 import BeautifulSoup, Tag
from typing import List

from parser_models import Section, Subsection, Link

log = logging.getLogger("section_parser")

KNOWN_SECTIONS = {
    "the drop",
    "screen share",
    "crowdsourced",
    "what we're watching",
    "signing off",
}


def clean_text(text: str) -> str:
    return " ".join(text.replace("\xa0", " ").split())


def extract_links(tag: Tag) -> list[Link]:
    links = []
    for a in tag.find_all("a", href=True):
        label = clean_text(a.get_text())
        url = a["href"]
        links.append(Link(label=label, url=url))
        a.replace_with(label)
    return links


def is_section_heading(text: str) -> bool:
    return clean_text(text).lower().rstrip(":") in KNOWN_SECTIONS


def parse_html(html: str) -> List[Section]:
    soup = BeautifulSoup(html, "html.parser")

    sections: List[Section] = []
    current = Section("Introduction", [])
    sections.append(current)

    # Running set of all link labels seen so far — avoids O(n²) re-scan
    all_link_labels: set[str] = set()

    for el in soup.find_all(["p", "h1", "h2", "h3", "strong"]):
        text = clean_text(el.get_text())
        if not text:
            continue

        if is_section_heading(text):
            norm = clean_text(text)
            if norm.lower() == current.title.lower():
                continue
            current = Section(norm, [])
            sections.append(current)
            continue

        links = extract_links(el)
        cleaned_text = clean_text(el.get_text())

        # Skip standalone text that duplicates a link label already seen
        # (Installer link-list pattern: label appears as plain <p> before the <a>)
        if cleaned_text and not links:
            if cleaned_text.lower() in all_link_labels:
                continue

        if cleaned_text or links:
            current.subsections.append(Subsection(text=cleaned_text, links=links))
            if links:
                all_link_labels.update(l.label.lower() for l in links)

    return sections

from parser_models import Section, Subsection


def _normalize(text: str) -> str:
    return " ".join(text.lower().split())


def _render_links_only(sub: Subsection) -> list[str]:
    lines = ["Links:"]
    for link in sub.links:
        lines.append(f"- {link.label}")
    lines.append("")
    return lines


def _render_mixed(subs: list[Subsection], i: int) -> tuple[list[str], int]:
    """
    Text-only subsection(s) followed by a links-only subsection.
    If the text buffer exactly matches the link labels, suppress the text
    and render only the links (Installer link-list dedup pattern).
    Returns (lines, new_i).
    """
    j = i
    text_buffer: list[str] = []

    while j < len(subs) and subs[j].text and not subs[j].links:
        text_buffer.append(_normalize(subs[j].text))
        j += 1

    if j < len(subs) and subs[j].links:
        link_labels = [_normalize(l.label) for l in subs[j].links]
        if text_buffer == link_labels:
            lines = ["Links:"]
            for link in subs[j].links:
                lines.append(f"- {link.label}")
            lines.append("")
            return lines, j + 1

    # No match — render the current subsection as plain text
    return [subs[i].text, ""], i + 1


def _render_normal(sub: Subsection) -> list[str]:
    lines: list[str] = []
    if sub.text:
        lines.extend([sub.text, ""])
    if sub.links:
        lines.append("Links:")
        for link in sub.links:
            lines.append(f"- {link.label}")
        lines.append("")
    return lines


def render_sections(sections: list[Section]) -> str:
    lines: list[str] = []

    for section in sections:
        lines.append(f"\n## {section.title}\n")

        subs = section.subsections
        i = 0

        while i < len(subs):
            sub = subs[i]

            if sub.links and not sub.text.strip():
                lines.extend(_render_links_only(sub))
                i += 1
            elif sub.text and not sub.links:
                new_lines, i = _render_mixed(subs, i)
                lines.extend(new_lines)
            else:
                lines.extend(_render_normal(sub))
                i += 1

    return "\n".join(lines).strip()

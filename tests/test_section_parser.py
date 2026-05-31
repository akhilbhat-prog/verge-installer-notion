import sys
from pathlib import Path

# Add project root to PYTHONPATH
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from section_parser import parse_html


HTML_DIR = Path("artifacts/emails")


def test_section_parsing():
    html_files = list(HTML_DIR.glob("*.html"))
    assert html_files, "No HTML files found. Run pipeline preview first."

    html = html_files[0].read_text(encoding="utf-8")
    sections = parse_html(html)

    assert sections, "No sections parsed"

    print("✅ Section parsing OK")
    for s in sections:
        print(f"- {s.title} ({len(s.subsections)} subsections)")


if __name__ == "__main__":
    test_section_parsing()

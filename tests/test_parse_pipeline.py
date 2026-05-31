import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from parse_pipeline import parse_html_file

HTML_DIR = ROOT / "artifacts" / "emails"


def test_full_parse_pipeline():
    html_files = list(HTML_DIR.glob("*.html"))
    assert html_files, "No HTML files found. Run pipeline.py preview first."

    html_path = html_files[0]
    parsed_path, rendered_path = parse_html_file(html_path)

    assert parsed_path.exists(), "Parsed JSON file not created"
    assert rendered_path.exists(), "Rendered preview file not created"

    rendered = rendered_path.read_text(encoding="utf-8")
    lowered = rendered.lower()

    assert rendered.strip(), "Rendered preview is empty"
    assert "http" not in lowered, "Raw URLs should not appear"

    forbidden_phrases = [
        "a weekly newsletter by david pierce",
        "you’re receiving this email",
        "this email was sent to",
        "vox media has affiliate partnerships",
        "ethics policy",
        "privacy policy",
        "terms of service",
        "unsubscribe",
        "all rights reserved",
        "vox media,",
    ]

    for phrase in forbidden_phrases:
        assert phrase not in lowered, f"Found forbidden text: {phrase}"

    print("✅ Full parse pipeline OK")
    print("Rendered preview (first 500 chars):")
    print(rendered)


if __name__ == "__main__":
    test_full_parse_pipeline()

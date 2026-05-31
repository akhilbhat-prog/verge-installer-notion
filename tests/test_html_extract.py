from pathlib import Path

EMAIL_DIR = Path("artifacts/emails")


def test_html_artifacts_exist_and_valid():
    html_files = list(EMAIL_DIR.glob("*.html"))

    assert html_files, "No HTML artifacts found. Run pipeline.py preview first."

    html_path = html_files[0]
    content = html_path.read_text(encoding="utf-8")

    assert content.strip(), "HTML file is empty"
    assert (
        "<html" in content.lower()
        or "<body" in content.lower()
        or "<pre" in content.lower()
    ), "HTML content does not look valid"

    print("✅ HTML artifact exists and looks valid")
    print("File:", html_path.name)
    print("Preview (first 500 chars):")
    print(content[:500])


if __name__ == "__main__":
    test_html_artifacts_exist_and_valid()

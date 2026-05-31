import sys
from pathlib import Path

# Add project root to PYTHONPATH
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def test_config_loads():
    try:
        import config
    except Exception as e:
        raise AssertionError(f"config.py failed to load: {e}")

    assert config.YAHOO_EMAIL, "YAHOO_EMAIL not set"
    assert config.YAHOO_APP_PASSWORD, "YAHOO_APP_PASSWORD not set"
    assert config.IMAP_HOST
    assert config.IMAP_PORT
    assert config.DEFAULT_FOLDER
    assert config.IST is not None

    print("✅ config.py loaded successfully")


if __name__ == "__main__":
    test_config_loads()

import sys
from pathlib import Path
import logging

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from logging_setup import setup_logging


def test_logging():
    setup_logging(logging.DEBUG)
    log = logging.getLogger("test_logging")

    log.debug("DEBUG test message")
    log.info("INFO test message")
    log.error("ERROR test message")

    print("✅ logging emitted messages (check console and artifacts/pipeline.log)")


if __name__ == "__main__":
    test_logging()

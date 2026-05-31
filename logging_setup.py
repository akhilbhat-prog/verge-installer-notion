import logging


def setup_logging(level=logging.INFO):
    root = logging.getLogger()
    root.setLevel(level)

    if root.handlers:
        return

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    console = logging.StreamHandler()
    console.setFormatter(formatter)

    file = logging.FileHandler("artifacts/pipeline.log", encoding="utf-8")
    file.setFormatter(formatter)

    root.addHandler(console)
    root.addHandler(file)

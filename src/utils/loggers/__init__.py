import logging

from .multiline import MultilineLogger

__all__ = ["setup_logger", "MultilineLogger"]


def setup_logger(level: int = logging.INFO) -> None:
    logging.basicConfig(
        format="%(asctime)s %(levelname)s | %(name)s: %(message)s",
        datefmt="[%H:%M:%S]",
        level=level,
    )

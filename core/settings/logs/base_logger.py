import logging
from typing import Optional
from logging.handlers import RotatingFileHandler


def setup_logger(name: str, filename: Optional[str] = None, level=logging.DEBUG) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - [%(name)s] - (%(filename)s:%(lineno)d) - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Console Handler (Sempre ativo para exibir no terminal)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File Handler Rotativo (Mantido apenas caso algum arquivo seja explicitamente informado no futuro)
    if filename:
        file_handler = RotatingFileHandler(filename, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
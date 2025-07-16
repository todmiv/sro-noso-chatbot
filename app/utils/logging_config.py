import logging
import structlog
from config.settings import config

def _get_log_level(level_str: str) -> int:
    """Convert string log level to logging constant."""
    level_map = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }
    level = level_map.get(level_str.upper())
    if level is None:
        raise ValueError(f"Invalid log level: {level_str}")
    return level

def setup_logging() -> None:
    log_level = _get_log_level(config.log_level)
    logging.basicConfig(level=log_level)
    structlog.configure(
        wrapper_class=structlog.make_filtering_bound_logger(log_level)
    )

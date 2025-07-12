import logging
import structlog
from config.settings import config

def setup_logging() -> None:
    logging.basicConfig(level=config.log_level)
    structlog.configure(
        wrapper_class=structlog.make_filtering_bound_logger(config.log_level)
    )

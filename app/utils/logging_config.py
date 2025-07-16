import logging
import structlog
from config.settings import config

def setup_logging() -> None:
    """Configure application logging."""
    try:
        logging.basicConfig(
            level=logging.INFO,  # Using numeric constant directly
            format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
            handlers=[logging.StreamHandler()]
        )
        
        structlog.configure(
            wrapper_class=structlog.make_filtering_bound_logger(logging.INFO)
        )
    except Exception as e:
        logging.error(f"Failed to configure logging: {e}")
        raise

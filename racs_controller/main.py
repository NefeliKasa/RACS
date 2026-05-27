
from watcher import watch_racs_configs
from utils.logging_config import setup_logger

logger = setup_logger(__name__)


def main():
    logger.info("Running RACS Controller.")
    watch_racs_configs() 


if __name__ == "__main__":
    main()

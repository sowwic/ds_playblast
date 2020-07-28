import logging.config
import logging.handlers
from dsPlayblast import util


def setup_logging():
    log_file = "playblast.log"
    # Formatters
    brief_formatter = logging.Formatter(fmt="%(levelname)s | %(message)s", datefmt="%Y-%m-%d %H:%M")
    verbose_formatter = logging.Formatter(fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s")
    # Handlers
    rfile_handler = logging.handlers.RotatingFileHandler(log_file, mode="a", maxBytes=1024, backupCount=0, delay=0)
    rfile_handler.setLevel("DEBUG")
    rfile_handler.setFormatter(verbose_formatter)
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel("DEBUG")
    stream_handler.setFormatter(brief_formatter)

    # Root logger
    logging.root.setLevel("DEBUG")
    logging.root.addHandler(stream_handler)
    logging.root.addHandler(rfile_handler)


if __name__ == "__main__":
    setup_logging()
    logging.root.info("Root logger")

import logging.config
from dsPlayblast import util


def setup_logging():
    log_file = "playblast.log"
    config_file = util.resource_path("configs/logging_config.ini")
    logging.config.fileConfig(config_file, defaults={'logfilename': log_file}, disable_existing_loggers=False)


if __name__ == "__main__":
    print(util.resource_path("logging_config.ini"))

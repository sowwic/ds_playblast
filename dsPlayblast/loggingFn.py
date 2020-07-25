import os
import logging.config


def setup_logging():
    log_file = "playblast.log"
    config_file = os.path.join(os.getcwd(), "dsPlayblast", "configs", "logging_config.ini")
    logging.config.fileConfig(config_file, defaults={'logfilename': log_file}, disable_existing_loggers=False)

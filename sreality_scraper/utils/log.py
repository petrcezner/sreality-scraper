import logging
import os
import sys
from pathlib import Path, PurePath

import colorlog


def init_logger(dunder_name, testing_mode) -> logging.Logger:
    parent_path = os.path.dirname(sys.modules['__main__'].__file__)
    log_format = (
        '%(asctime)s - '
        '%(name)s - '
        '%(funcName)s - '
        '%(levelname)s - '
        '%(message)s'
    )
    bold_seq = '\033[1m'
    colorlog_format = (
        f'{bold_seq} '
        '%(log_color)s '
        f'{log_format}'
    )
    colorlog.basicConfig(format=colorlog_format)
    logger = logging.getLogger(dunder_name)

    if testing_mode:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    log_filename = parent_path + '/logs/app.log'
    os.makedirs(os.path.dirname(log_filename), exist_ok=True)
    fh = logging.FileHandler(log_filename, mode='w', encoding=None, delay=False)
    formatter = logging.Formatter(log_format)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    return logger


def set_level(logger, debug):
    if debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    return logger

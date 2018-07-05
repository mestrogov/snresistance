# -*- coding: utf-8 -*-

import logging
from app import config


try:
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    logging.addLevelName(logging.DEBUG, '\x1b[32m%s\x1b[0m' % logging.getLevelName(logging.DEBUG))
    logging.addLevelName(logging.INFO, '\x1b[34m%s\x1b[0m' % logging.getLevelName(logging.INFO))
    logging.addLevelName(logging.WARNING, '\x1b[33m%s\x1b[0m' % logging.getLevelName(logging.WARNING))
    logging.addLevelName(logging.ERROR, '\x1b[31m%s\x1b[0m' % logging.getLevelName(logging.ERROR))
    logging.addLevelName(logging.CRITICAL, '\x1b[31;1m%s\x1b[0m' % logging.getLevelName(logging.CRITICAL))

    if config.developerMode:
        formatter = logging.Formatter('%(threadName)s/%(filename)s:%(lineno)d/%(funcName)s() | %(asctime)s | '
                                      '%(levelname)s  >  %(message)s', '%d.%m.%y, %H:%M:%S')
    else:
        formatter = logging.Formatter('%(asctime)s | %(levelname)s  >  %(message)s',
                                      '%d.%m.%y, %H:%M:%S')

    """
    fileHandler = logging.FileHandler("latest.log")
    fileHandler.setLevel(logging.INFO)
    fileHandler.setFormatter(formatter)
    logger.addHandler(fileHandler)
    """

    consoleHandler = logging.StreamHandler()
    if config.developerMode:
        consoleHandler.setLevel(logging.DEBUG)
    else:
        consoleHandler.setLevel(logging.INFO)
    consoleHandler.setFormatter(formatter)
    logger.addHandler(consoleHandler)
except:
    logging.critical("Exception has been occurred while trying to set up logging settings.", exc_info=True)

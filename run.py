# -*- coding: utf-8 -*-

from app import logging
from app import config as config
from app.bot import bot_initialize as botInitialize
from app.bot import bot_configuration as botConfiguration
from app.remote.postgresql import Psql as psql
from app.remote.redis import Redis as redis
from app.channels.polling import polling as channelPolling
from telegram.ext import Updater
import logging
import asyncio
import time


if __name__ == "__main__":
    try:
        if config.developerMode:
            ignoredModulesLoggers = []
            # noinspection PyUnresolvedReferences
            for logger in logging.Logger.manager.loggerDict:
                if str(logger).startswith("telegram"):
                    pass
                else:
                    ignoredModulesLoggers.extend([logger])
                    logging.getLogger(logger).setLevel(logging.WARNING)
            logging.debug("Ignoring these Modules' Loggers: " + str(ignoredModulesLoggers) + '.')

        asyncio.get_event_loop().run_until_complete(psql.connection())
        asyncio.get_event_loop().run_until_complete(redis.connection())

        logging.debug("Bot Configuration: " + str(botConfiguration()))
        botUpdater = botInitialize()

        channelPolling()

        try:
            while True:
                time.sleep(0.1)
        except KeyboardInterrupt:
            botUpdater.idle()
    except Exception as e:
        logging.critical("Exception has been occurred while trying to run the application.", exc_info=True)

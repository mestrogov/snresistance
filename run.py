# -*- coding: utf-8 -*-

from app import logging
from app import handlers
from app import config as config
from app.bot import bot as bot
from app.remote.postgresql import Psql as psql
from app.remote.redis import Redis as redis
from app.channels.polling import polling as channelPolling
from threading import Thread
import logging
import asyncio
import time


if __name__ == "__main__":
    try:
        if config.developerMode:
            ignoredModulesLoggers = []
            # noinspection PyUnresolvedReferences
            for logger in logging.Logger.manager.loggerDict:
                ignoredModulesLoggers.extend([logger])
                logging.getLogger(logger).setLevel(logging.WARNING)
            logging.debug("Ignoring these Modules' Loggers: " + str(ignoredModulesLoggers) + '.')

        asyncio.get_event_loop().run_until_complete(psql.connection())
        asyncio.get_event_loop().run_until_complete(redis.connection())

        logging.debug("Bot Settings: " + str(bot.get_me()))

        # noinspection PyTypeChecker
        cPolling = Thread(target=channelPolling)
        cPolling.setDaemon(True)
        cPolling.start()

        # noinspection PyArgumentList
        bPolling = Thread(target=bot.polling, kwargs={'none_stop': True})
        bPolling.setDaemon(True)
        bPolling.start()

        try:
            while True:
                time.sleep(0.1)
        except:
            pass
    except Exception as e:
        logging.critical("Exception has been occurred while trying to run the application.", exc_info=True)

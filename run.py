# -*- coding: utf-8 -*-

from app import logging
from app import config as config
from app.bot import bot_initialize as bot_initialize
from app.bot import bot_configuration as bot_configuration
from app.remote.postgresql import Psql as psql
from app.remote.redis import Redis as redis
from telegram.ext import Updater
import logging
import asyncio
import time


if __name__ == "__main__":
    try:
        ignoredModulesLoggers = []
        for logger in logging.Logger.manager.loggerDict:
            ignoredModulesLoggers.extend([logger])
            logging.getLogger(logger).setLevel(logging.WARNING)
        if config.developerMode:
            logging.debug("Игнорирование логирования уровня INFO от следующих модулей: " +
                          str(ignoredModulesLoggers) + '.')

        asyncio.get_event_loop().run_until_complete(psql.create_tables())
        asyncio.get_event_loop().run_until_complete(psql.connection())
        asyncio.get_event_loop().run_until_complete(redis.connection())

        logging.debug("Конфигурация Бота: " + str(bot_configuration()))
        bot_updater = bot_initialize()

        try:
            while True:
                time.sleep(0.1)
        except KeyboardInterrupt:
            pass
    except Exception as e:
        logging.critical("Произошла ошибка при попытке запуска приложения.", exc_info=True)

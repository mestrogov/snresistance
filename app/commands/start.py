# -*- coding: utf-8 -*-

from app import logging
from app import config as config
from app.remote.postgresql import Psql as psql
from app.remote.redis import Redis as redis
from telegram.ext.dispatcher import run_async
import logging
import asyncio


@run_async
def start(bot, message):
    try:
        message = message.message
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        if "ru" not in message.from_user.language_code:
            bot.send_message(message.from_user.id,
                             "❗ Unfortunately, the bot doesn't speak your language. So if you are "
                             "not able to understand Russian, use an online translator such as Google Translate.")

        bot.send_message(message.from_user.id, config.startMessage, parse_mode="Markdown")
        loop.run_until_complete(
            redis.execute("SET", "status:{0}".format(message.from_user.id),
                          '{"status": "waiting", "method": "find_communities"}', "EX", 180))
    except Exception as e:
        try:
            bot.send_message(message.from_user.id,
                             "❗ Извините, что-то пошло не так, но в скором времени все исправится. "
                             "Попробуйте выполнить то же самое действие через некоторое время (10-15 минут).")
        except:
            pass

        logging.error("Exception has been occurred while trying to execute the method.", exc_info=True)
        return e

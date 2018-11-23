# -*- coding: utf-8 -*-

from app import logging
from app import config as config
from app.remote.redis import Redis as redis
from telegram.ext.dispatcher import run_async
import logging
import asyncio


@run_async
def cancel(bot, message):
    try:
        message = message.message
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        loop.run_until_complete(redis.execute("DEL", "status:{0}".format(message.from_user.id)))
        bot.send_message(message.from_user.id, "Вы успешно отменили текущую операцию.")
    except Exception as e:
        try:
            bot.send_message(message.from_user.id,
                             "❗ Извините, что-то пошло не так, но в скором времени все будет исправлено. "
                             "Попробуйте выполнить то же самое действие через некоторое время (10-15 минут).")
        except:
            pass

        logging.error("Exception has been occurred while trying to execute the method.", exc_info=True)
        return e

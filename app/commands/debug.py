# -*- coding: utf-8 -*-

from app import logging
from app.remote.postgresql import Psql as psql
from telegram.ext.dispatcher import run_async
import logging
import asyncio


@run_async
def debug(bot, message):
    try:
        message = message.message

        bot.send_message(message.from_user.id,
                         "Вот информация, которая может пригодиться при выявлении проблемы и не только ее."
                         "\n\nUser ID: `{0}`"
                         "\nMessage ID: `{1}`"
                         "\nLanguage Code: `{2}`".format(str(message.from_user.id), str(message.message_id),
                                                         str(message.from_user.language_code)), parse_mode="Markdown")
    except Exception as e:
        try:
            bot.send_message(message.from_user.id,
                             "❗ Извините, что-то пошло не так, но в скором времени все будет исправлено. "
                             "Попробуйте выполнить то же самое действие через некоторое время (10-15 минут).")
        except:
            pass

        logging.error("Exception has been occurred while trying to execute the method.", exc_info=True)
        return e

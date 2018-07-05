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
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        admin = loop.run_until_complete(psql.fetchrow(
            'SELECT admin FROM users WHERE id = $1;',
            message.from_user.id
        ))['admin']
        paid_account = loop.run_until_complete(psql.fetchrow(
            'SELECT paid_account FROM users WHERE id = $1;',
            message.from_user.id
        ))['paid_account']
        communities = loop.run_until_complete(psql.fetchrow(
            'SELECT communities FROM users WHERE id = $1;',
            message.from_user.id
        ))['communities']

        bot.send_message(message.from_user.id,
                         "Вот информация, которая может помочь людям с хорошими намерениями."
                         "\n\n*Не скидывайте ее тому, кому не доверяете, хотя здесь фактически нет конфиденциальной "
                         "информации, но зачем предоставлять лишнюю информацию людям?*"
                         "\n\n*Global:*"
                         "\nUser ID: `{0}`"
                         "\nMessage ID: `{1}`"
                         "\nLanguage Code: `{2}`"
                         "\n\n*Database:*"
                         "\nAdmin: `{3}`"
                         "\nPaid Account: `{4}`"
                         "\nCommunities: `{5}`".format(
                            str(message.from_user.id), str(message.message_id),
                            str(message.from_user.language_code), str(admin), str(paid_account), str(communities)
                         ), parse_mode="Markdown")
    except Exception as e:
        try:
            bot.send_message(message.from_user.id,
                             "❗ *Извините, что-то пошло не так, но в скором времени все будет исправлено. "
                             "Попробуйте выполнить то же самое действие через некоторое время (10-15 минут).*",
                             parse_mode="Markdown")
        except:
            pass

        logging.error("Exception has been occurred while trying to execute the method.", exc_info=True)
        return e

# -*- coding: utf-8 -*-

from app import logging
from app.remote.postgresql import Psql as psql
from app.remote.redis import Redis as redis
from ast import literal_eval
from telegram.ext.dispatcher import run_async
import logging
import asyncio


@run_async
def find_community(bot, message):
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        channel_links = []
        communities = str(message.text).replace('https', '').replace('http', '').replace('://', '').replace('www.', '')\
            .replace('vk.com/', '').split(';', 10)
        logging.debug(communities)

        for community_id in communities:
            channel_link = loop.run_until_complete(
                psql.fetchrow("SELECT chat_link FROM channels WHERE community_id = $1", str(community_id)))
            channel_links.extend([str(channel_link)])

        bot.send_message(message.from_user.id, "Отлично, все готово! Вот каналы сообществ, на которые Вы "
                                               "предоставили ссылки:")

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

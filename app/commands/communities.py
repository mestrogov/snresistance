# -*- coding: utf-8 -*-

from app import logging
from app.remote.postgresql import Psql as psql
from ast import literal_eval
from telegram.ext.dispatcher import run_async
import logging
import asyncio


@run_async
def add_community(bot, message):
    try:
        message = message.message
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        communities = []
        communities_old = loop.run_until_complete(psql.fetchrow(
            'SELECT communities FROM users WHERE id = $1;',
            message.from_user.id
        ))['communities']
        if communities_old:
            communities_old = literal_eval(communities_old)
            for elm in communities_old:
                communities.extend([elm])

        try:
            cm_url = message.text.split('vk.com/')[1]

            if cm_url in communities:
                bot.send_message(message.from_user.id,
                                 "В Ваших подписках уже есть такое сообщество, добавьте другое.")
            else:
                bot.send_message(message.from_user.id,
                                 "Вы успешно добавили новое сообщество в подписки! Надеюсь, оно хорошее (:")

                communities.extend([cm_url])
                loop.run_until_complete(psql.execute(
                    'UPDATE users SET "communities"=$1 WHERE "id"=$2 RETURNING "id", "admin", "paid_account", '
                    '"communities", "access_token";',
                    str(communities), message.from_user.id
                ))
        except Exception:
            bot.send_message(message.from_user.id,
                             "Упс! Похоже, что Вы указали ссылку в неправильном формате. "
                             "Пример правильной команды: `vk.com/examplecommunity`", parse_mode="Markdown")
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


@run_async
def remove_community(bot, message):
    try:
        message = message.message
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        communities = []
        communities_db = loop.run_until_complete(psql.fetchrow(
            'SELECT communities FROM users WHERE id = $1;',
            message.from_user.id
        ))['communities']
        # print(communities_db)
        if communities_db:
            communities_db = literal_eval(communities_db)
            for elm in communities_db:
                communities.extend([elm])

        try:
            cm_url = message.text.split('vk.com/')[1]

            if cm_url not in communities:
                bot.send_message(message.from_user.id,
                                 "В Ваших подписках нет такого сообщества.")
            else:
                bot.send_message(message.from_user.id,
                                 "Вы успешно отписались от сообщества!")

                communities.remove(cm_url)
                loop.run_until_complete(psql.execute(
                    'UPDATE users SET "communities"=$1 WHERE "id"=$2 RETURNING "id", "admin", "paid_account", '
                    '"communities", "access_token";',
                    str(communities), message.from_user.id
                ))
        except Exception:
            bot.send_message(message.from_user.id,
                             "Упс! Похоже, что Вы указали ссылку в неправильном формате. "
                             "Пример правильной команды: `vk.com/examplecommunity`", parse_mode="Markdown")
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

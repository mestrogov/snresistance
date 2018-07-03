# -*- coding: utf-8 -*-

from app import logging
from app import config as config
from app.remote.postgresql import Psql as psql
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
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
                             "❗ *Unfortunately, the bot doesn't speak your language. So if you are "
                             "not able to understand Russian, use an online translator such as Google Translate.*",
                             parse_mode="Markdown")

        bot.send_message(message.from_user.id, config.startMessage, parse_mode="Markdown")
        start_menu(bot, message)

        loop.run_until_complete(psql.execute(
            'INSERT INTO users("id") VALUES($1) RETURNING "id", "is_paid", "vk_token", "communities";',
            message.from_user.id
        ))
    except Exception as e:
        try:
            bot.send_message(message.from_user.id,
                             "❗ *Извините, что-то пошло не так, но в скором времени все исправится. "
                             "Попробуйте выполнить то же самое действие через некоторое время (10-15 минут).*",
                             parse_mode="Markdown")
        except:
            pass

        logging.error("Exception has been occurred while trying to execute the method.", exc_info=True)
        return e


@run_async
def start_menu(bot, message):
    try:
        logging.debug("Passed argument: " + str(message))

        markup = [[
            InlineKeyboardButton("Импортировать все мои сообщества", callback_data="start_vk_import")],
            [InlineKeyboardButton("Указать прямую ссылку на сообщество", callback_data="start_menu_direct_url")
             ]]
        markup = InlineKeyboardMarkup(markup)
        bot.send_message(message.from_user.id,
                         "Выберите способ, с помощью которого Вы хотите подписаться на первое сообщество ВКонтакте, "
                         "используя мои возможности.",
                         reply_markup=markup)
    except Exception as e:
        try:
            bot.send_message(message.from_user.id,
                             "❗ *Извините, что-то пошло не так, но в скором времени все исправится. "
                             "Попробуйте выполнить то же самое действие через некоторое время (10-15 минут).*",
                             parse_mode="Markdown")
        except:
            pass

        logging.error("Exception has been occurred while trying to execute the method.", exc_info=True)
        return e

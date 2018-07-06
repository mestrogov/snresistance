# -*- coding: utf-8 -*-

from app import logging
from app import config as config
from app.remote.postgresql import Psql as psql
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext.dispatcher import run_async
from shutil import copyfileobj
from os import remove
from secrets import token_hex
from calendar import timegm
from datetime import datetime
import logging
import asyncio
import requests


@run_async
def addchannel(bot, message):
    try:
        message = message.message
        markup = [[
            InlineKeyboardButton(text='Настроить канал', switch_inline_query="Initialize Channel: #{0}".format(
                str(message.text).replace("/addchannel ", "")
            ))
        ]]
        markup = InlineKeyboardMarkup(markup)
        bot.send_message(message.from_user.id,
                         "Благодарю за возникший интерес к созданию собственного канала для репостинга публикаций из "
                         "данного сообщества. Нажмите на кнопку ниже, чтобы продолжить.",
                         parse_mode="Markdown", reply_markup=markup)
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
def initializechannel(bot, message):
    try:
        message = message.channel_post
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        if "InitializeChannel|" in message.text:
            channel_data = message.text.replace("InitializeChannel|", "").strip().split("|")
            user_id = str(channel_data[0]).split("&", 1)[0]
            community_id = str(channel_data[0]).split("&", 1)[1]
            if community_id.startswith("public"):
                community_id = community_id.replace("public", "club", 1)

            access_token = loop.run_until_complete(psql.fetchrow(
                'SELECT access_token FROM users WHERE id = $1;',
                int(user_id)
            ))['access_token']

            community = requests.post("https://api.vk.com/method/groups.getById",
                                      data={
                                          "group_id": str(community_id),
                                          "fields": "description",
                                          "access_token": str(access_token),
                                          "v": "5.80"
                                      }).json()['response'][0]

            channel_id = message.chat.id

            try:
                bot.set_chat_title(channel_id, community['name'])
            except:
                bot.send_message(user_id,
                                 "Не удалось изменить имя канала.")
                return

            try:
                lfile_name = str(token_hex(16)) + '.png'
                lfile_res = requests.get(community['photo_200'], stream=True)
                with open(lfile_name, 'wb') as lfile_out:
                    copyfileobj(lfile_res.raw, lfile_out)
                lphoto = open(lfile_name, 'rb')
                remove(lfile_name)
                bot.set_chat_photo(channel_id, lphoto)
            except:
                bot.send_message(user_id,
                                 "Не удалось установить логотип канала.")
                return

            try:
                pin_id = bot.send_message(channel_id, str(community['description']))
                bot.pin_chat_message(channel_id, pin_id.json['message_id'])
            except:
                pass
                """
                bot.send_message(user_id,
                                 "Не удалось отправить сообщение и закрепить его в канале.")
                return
                """

            try:
                bot.set_chat_description(channel_id, "Тестовое описание, чтобы проверить права Бота.")
            except:
                bot.send_message(user_id,
                                 "Не удалось изменить описание канала.")
                return

            bot.set_chat_description(channel_id, config.channelDescription)

            loop.run_until_complete(psql.execute(
                'INSERT INTO channels("id", "owner_id", "community_id") '
                'VALUES($1, $2, $3) RETURNING "id", "owner_id", "community_id";',
                int(channel_id), int(user_id), int(community['id'])
             ))

            bot.send_message(int(user_id),
                             "Ваш канал успешно настроен и готов для получения новых постов.")
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

# -*- coding: utf-8 -*-

from app import logging
from app import config as config
from app.bot import bot as bot
from app.remote.postgresql import Psql as psql
from shutil import copyfileobj
from os import remove
from secrets import token_hex
from calendar import timegm
from telebot import types
from datetime import datetime
import logging
import asyncio
import requests


def addchannel(message):
    try:
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton(text='Превратить канал',
                                       switch_inline_query="!initiateChannel 1243|1234"),
        )
        bot.send_message(message.from_user.id,
                         "Вы решили создать канал, добавьте меня в него и напишите команду: "
                         "`/initchannel@SNResistance {0}_id`",
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


def initiatechannel(message):
    try:
        print("----------")
        print("Channel Name: " + str(message.chat.title))
        print("Channel ID: " + str(message.chat.id))

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        if "!initiateChannel" in message.text:
            command = message.text.replace("!initiateChannel", "").strip().split("|")
            if command[1].startswith("public"):
                command[1] = command[1].replace("public", "club", 1)

            user_id = int(command[0])
            user_vktoken = loop.run_until_complete(psql.fetchrow(
                'SELECT vk_token FROM users WHERE id = $1;',
                int(user_id)
            ))['vk_token']

            community = requests.post("https://api.vk.com/method/groups.getById",
                                      data={
                                          "group_id": str(command[1]),
                                          "fields": "description",
                                          "access_token": str(user_vktoken),
                                          "v": "5.78"
                                      }).json()['response'][0]

            channel_id = message.chat.id
            initiation_date = timegm(datetime.utcnow().utctimetuple())

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
                'INSERT INTO channels("id", "owner_id", "community_id", "initiation_date") '
                'VALUES($1, $2, $3, $4) RETURNING "id", "owner_id", "community_id", "initiation_date";',
                int(channel_id), int(user_id), int(community['id']), int(initiation_date)
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

# -*- coding: utf-8 -*-

from app import remote
from app import logging
from app.bot import bot as bot
from app.remote.postgresql import Psql as psql
from app.remote.redis import Redis as redis
from app import commands as commands
from telebot import types
from datetime import datetime
import logging
import asyncio
import requests


def callback_query(call):
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        if call.message:
            if call.data == "exit_to_start_menu":
                bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
                commands.start.startmenu(message=call)
            if call.data == "start_vk_import":
                markup = types.InlineKeyboardMarkup(row_width=1)
                markup.add(
                    types.InlineKeyboardButton("Импортировать", url="google.com"),
                    types.InlineKeyboardButton("❌  Отменить", callback_data="exit_to_start_menu")
                )
                bot.edit_message_text(
                    "Обратите внимание, что при импортировании сообществ будет автоматически "
                    "запрошен доступ к стене, это необходимо для получения самих публикаций. "
                    "Также это необходимо, чтобы увеличить максимальное количество групп до 30 "
                    "и понизить время обновления до 15 минут. Если Вы хотите импортировать больше "
                    "30 сообществ, то необходимо приобрести UNIQUE (подробнее о ней в FAQ).",
                    parse_mode="Markdown", reply_markup=markup,
                    chat_id=call.from_user.id, message_id=call.message.message_id
                )
            elif call.data == "start_menu_direct_url":
                bot.edit_message_text(
                    "Отлично! Теперь отправьте мне ссылку на сообщество с помощью команды /add.",
                    parse_mode="Markdown", chat_id=call.from_user.id, message_id=call.message.message_id
                )
            elif call.data == "start_menu_next":
                logging.warning("The temporary stub for callback with start_menu_next data.")
            elif call.data.startswith("channel_counters_"):
                data_splitted = call.data.replace("channel_counters_", "", 1).split("|")

                cached = loop.run_until_complete(
                    redis.execute("EXISTS", "channel_counters|{0}".format(str(data_splitted[1]))))
                cached = int(cached)
                if cached:
                    counters_data_splitted = loop.run_until_complete(redis.execute("GET", "channel_counters|{0}".format(
                        str(data_splitted[1])
                    ))).split("_")
                else:
                    owner_id = loop.run_until_complete(psql.fetchrow('SELECT owner_id FROM channels WHERE id = $1;',
                                                                     int(call.message.json['chat']['id'])))['owner_id']
                    token = loop.run_until_complete(psql.fetchrow(
                        'SELECT vk_token FROM users WHERE id = $1;',
                        int(owner_id)
                    ))['vk_token']

                    ids_data_splitted = data_splitted[1].split("_")
                    post_counters = requests.post("https://api.vk.com/method/wall.getById",
                                                  data={
                                                      "posts": str(
                                                          str(ids_data_splitted[1]) + "_" +
                                                          str(ids_data_splitted[2])
                                                      ),
                                                      "copy_history_depth": 1,
                                                      "extended": 1,
                                                      "access_token": token,
                                                      "v": "5.78"
                                                  }).json()['response']['items'][0]
                    counters_data_splitted = "{0}_{1}_{2}_{3}_{4}".format(
                        str(post_counters['date']),
                        str(post_counters['likes']['count']),
                        str(post_counters['comments']['count']),
                        str(post_counters['reposts']['count']),
                        str(post_counters['views']['count'])
                    ).split("_")

                if data_splitted[0] == "time":
                    bot.answer_callback_query(callback_query_id=call.id,
                                              text="🕒 Время публикации данного поста: {0} MSK.".format(
                                                  str(datetime.fromtimestamp(
                                                      int(counters_data_splitted[0])).strftime("%H:%M"))),
                                              show_alert=True)
                elif data_splitted[0] == "likes":
                    bot.answer_callback_query(callback_query_id=call.id,
                                              text="💖 Общее количество лайков: {0}.".format(
                                                  str(counters_data_splitted[1]), show_alert=True))
                elif data_splitted[0] == "comments":
                    bot.answer_callback_query(callback_query_id=call.id,
                                              text="💬 Общее количество комментариев: {0}.".format(
                                                  str(counters_data_splitted[2]), show_alert=True))
                elif data_splitted[0] == "reposts":
                    bot.answer_callback_query(callback_query_id=call.id,
                                              text="🔁 Общее количество репостов: {0}.".format(
                                                  str(counters_data_splitted[3]), show_alert=True))
                elif data_splitted[0] == "views":
                    bot.answer_callback_query(callback_query_id=call.id,
                                              text="👁 Общее количество просмотров: {0}.".format(
                                                  str(counters_data_splitted[4]), show_alert=True))
                else:
                    bot.answer_callback_query(callback_query_id=call.id,
                                              text="❗ Ой, что-то пошло не так. Попробуйте через некоторое время.",
                                              show_alert=True)

            bot.answer_callback_query(callback_query_id=call.id, show_alert=False)
    except Exception as e:
        try:
            bot.send_message(call.from_user.id,
                             "❗ *Извините, что-то пошло не так, но в скором времени все исправится. "
                             "Попробуйте выполнить то же самое действие через некоторое время (10-15 минут).*",
                             parse_mode="Markdown")
        except:
            pass

        logging.error("Exception has been occurred while trying to execute the method.", exc_info=True)
        return e

# -*- coding: utf-8 -*-

from app import logging
from app.utils.post_statistics import statistics as postStatistics
from app.remote.postgresql import Psql as psql
from app.remote.redis import Redis as redis
from telegram.ext.dispatcher import run_async
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from app.commands.start import start_menu as startMenu
from datetime import datetime
import logging
import asyncio
import requests


@run_async
def callback_query(bot, call):
    try:
        call = call.callback_query
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        if call.message:
            if call.data == "exit_to_start_menu":
                bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
                # noinspection PyUnresolvedReferences
                startMenu(bot, call)
            if call.data == "start_vk_import":
                markup = [
                    [InlineKeyboardButton("Импортировать", url="google.com")],
                    [InlineKeyboardButton("❌  Отменить", callback_data="exit_to_start_menu")]
                ]
                markup = InlineKeyboardMarkup(markup)

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
                counter_data_splitted = data_splitted[2]

                if data_splitted[0] == "time":
                    bot.answer_callback_query(callback_query_id=call.id,
                                              text="🕒 Время публикации данного поста: {0} MSK.".format(
                                                  str(datetime.fromtimestamp(
                                                      int(counter_data_splitted)).strftime("%d.%m.%y, %H:%M:%S"))),
                                              show_alert=True, cache_time=30)
                elif data_splitted[0] == "likes":
                    bot.answer_callback_query(callback_query_id=call.id,
                                              text="💖 Количество лайков: {0}.".format(
                                                  str(counter_data_splitted), show_alert=True, cache_time=30))
                elif data_splitted[0] == "comments":
                    bot.answer_callback_query(callback_query_id=call.id,
                                              text="💬 Количество комментариев: {0}.".format(
                                                  str(counter_data_splitted), show_alert=True, cache_time=30))
                elif data_splitted[0] == "reposts":
                    bot.answer_callback_query(callback_query_id=call.id,
                                              text="🔁 Количество репостов: {0}.".format(
                                                  str(counter_data_splitted), show_alert=True, cache_time=30))
                elif data_splitted[0] == "views":
                    bot.answer_callback_query(callback_query_id=call.id,
                                              text="👁 Количество просмотров: {0}.".format(
                                                  str(counter_data_splitted), show_alert=True, cache_time=30))
                elif data_splitted[0] == "poll_answers":
                    bot.answer_callback_query(callback_query_id=call.id,
                                              text="❎ Количество голосов за данный вариант ответа: {0} 👍🏻.".format(
                                                  str(counter_data_splitted), show_alert=True, cache_time=30))
            elif call.data.startswith("channel_refresh_counters"):
                data_splitted = call.data.replace("channel_refresh_counters_", "", 1).split("|")

                cached = loop.run_until_complete(
                    redis.execute("TTL", "channel_counters|{0}".format(str(data_splitted[1]))))
                if int(cached) <= 0:
                    owner_id = loop.run_until_complete(psql.fetchrow('SELECT owner_id FROM channels WHERE id = $1;',
                                                                     int(call.message.chat.id)))['owner_id']
                    token = loop.run_until_complete(psql.fetchrow(
                        'SELECT vk_token FROM users WHERE id = $1;',
                        int(owner_id)
                    ))['vk_token']

                    ids_data_splitted = data_splitted[1].split("_")
                    post = requests.post("https://api.vk.com/method/wall.getById",
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
                    stats_status = postStatistics(bot, posts=post, chat_id=call.message.chat.id,
                                                  message_id=call.message.message_id, mtype="update")
                    if stats_status == "OK" or stats_status == "IS NOT MODIFIED":
                        bot.answer_callback_query(callback_query_id=call.id,
                                                  text="✅ Статистика данной публикации была успешно обновлена! "
                                                       "Обратите внимание, что клиенту потребуется до 30 секунд для "
                                                       "отображения новых результатов при нажатии на кнопку.",
                                                  show_alert=True, cache_time=30)
                    else:
                        bot.answer_callback_query(callback_query_id=call.id,
                                                  text="❌ Что-то пошло не так при попытке обновлении статистики данной "
                                                       "публикации, попробуйте позже.",
                                                  show_alert=True, cache_time=30)
                else:
                    bot.answer_callback_query(callback_query_id=call.id,
                                              text="❌ Статистика данной публикации была недавно обновлена, попробуйте "
                                                   "немного позже.",
                                              show_alert=True, cache_time=30)
            bot.answer_callback_query(callback_query_id=call.id, show_alert=False)
    except Exception as e:
        logging.error("Exception has been occurred while trying to execute the method.", exc_info=True)
        return e

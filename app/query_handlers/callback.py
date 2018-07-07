# -*- coding: utf-8 -*-

from app import logging
from app.utils.post_statistics import statistics as postStatistics
from app.remote.postgresql import Psql as psql
from app.remote.redis import Redis as redis
from telegram.ext.dispatcher import run_async
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from app.commands.start import start_menu as startMenu
from datetime import datetime
from time import time
import logging
import asyncio
import requests


def refresh_stats(bot, call):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    stats = call.data.split("|")
    pdata = stats[1]
    expired = stats[2]

    if int(time()) >= int(expired):
        owner_id = loop.run_until_complete(psql.fetchrow('SELECT owner_id FROM channels WHERE id = $1;',
                                                         int(call.message.chat.id)))['owner_id']
        access_token = loop.run_until_complete(psql.fetchrow(
            'SELECT access_token FROM users WHERE id = $1;',
            int(owner_id)
        ))['access_token']

        pdata_splitted = str(pdata).split("&")
        post = requests.post("https://api.vk.com/method/wall.getById",
                             data={
                                 "posts": str(
                                     str(pdata_splitted[0]) + "_" +
                                     str(pdata_splitted[1])
                                 ),
                                 "copy_history_depth": 1,
                                 "extended": 1,
                                 "access_token": access_token,
                                 "v": "5.80"
                             }).json()['response']['items'][0]
        update_status = postStatistics(bot, posts=post, chat_id=call.message.chat.id,
                                       message_id=call.message.message_id, mtype="update")
        if update_status == "OK" or update_status == "IS NOT MODIFIED":
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


@run_async
def callback(bot, call):
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
                pass
            elif call.data.startswith("channel_counters"):
                counter = call.data.split("|")
                counter_name = counter[1]
                counter_amount = counter[2]
                if counter_name == "time":
                    bot.answer_callback_query(callback_query_id=call.id,
                                              text="🕒 Время публикации данного поста: {0} MSK.".format(
                                                  str(datetime.fromtimestamp(
                                                      int(counter_amount)).strftime("%d.%m.%y, %H:%M:%S"))),
                                              show_alert=True, cache_time=30)
                elif counter_name == "likes":
                    bot.answer_callback_query(callback_query_id=call.id,
                                              text="💖 Количество лайков: {0}.".format(
                                                  str(counter_amount)), show_alert=True, cache_time=30)
                elif counter_name == "comments":
                    bot.answer_callback_query(callback_query_id=call.id,
                                              text="💬 Количество комментариев: {0}.".format(
                                                  str(counter_amount)), show_alert=True, cache_time=30)
                elif counter_name == "reposts":
                    bot.answer_callback_query(callback_query_id=call.id,
                                              text="🔁 Количество репостов: {0}.".format(
                                                  str(counter_amount)), show_alert=True, cache_time=30)
                elif counter_name == "views":
                    bot.answer_callback_query(callback_query_id=call.id,
                                              text="👁 Количество просмотров: {0}.".format(
                                                  str(counter_amount)), show_alert=True, cache_time=30)
                elif counter_name == "poll":
                    try:
                        poll_name = loop.run_until_complete(redis.execute("GET", str("poll&" + str(counter_amount))))
                    except AttributeError:
                        logging.debug("AttributeError Exception has been occurred, most likely this poll "
                                      "isn't in the cache.", exc_info=True)
                        refresh_stats(bot, call)
                        return
                    bot.answer_callback_query(callback_query_id=call.id,
                                              text="📋 Название голосования: {0}.".format(
                                                  str(poll_name[0:170])), show_alert=True, cache_time=30)
                elif counter_name == "poll_ans":
                    try:
                        poll_answer = loop.run_until_complete(redis.execute(
                            "GET", str("poll_answer&" + str(counter_amount)))).split("&")
                    except AttributeError:
                        logging.debug("AttributeError Exception has been occurred, most likely this poll answer "
                                      "isn't in the cache.", exc_info=True)
                        refresh_stats(bot, call)
                        return
                    bot.answer_callback_query(callback_query_id=call.id,
                                              text="❎ Количество голосов за {0}: {1} голосов.".format(
                                                  str(poll_answer[0][0:140]), str(poll_answer[1])),
                                              show_alert=True, cache_time=30)
            elif call.data.startswith("channel_refresh_stats"):
                refresh_stats(bot, call)
            bot.answer_callback_query(callback_query_id=call.id, show_alert=False)
    except Exception as e:
        logging.error("Exception has been occurred while trying to execute the method.", exc_info=True)
        return e

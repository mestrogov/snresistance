# -*- coding: utf-8 -*-

from app import logging
from app.utils.post_statistics import statistics as post_statistics
from app.remote.postgresql import Psql as psql
from app.remote.redis import Redis as redis
from telegram.ext.dispatcher import run_async
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime
from time import time
import logging
import asyncio
import requests


def refresh_stats(bot, call, expired=None):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    stats = call.data.split("|", 1)
    if not expired:
        expired = stats[1]

    if int(time()) >= int(expired):
        owner_id = loop.run_until_complete(psql.fetchrow('SELECT owner_id FROM channels WHERE id = $1;',
                                                         int(call.message.chat.id)))['owner_id']
        community_id = loop.run_until_complete(
            psql.fetchrow('SELECT community_id FROM posts WHERE chat_id = $1 AND message_id = $2;',
                          int(call.message.chat.id), int(call.message.message_id)))['community_id']
        post_id = loop.run_until_complete(
            psql.fetchrow('SELECT post_id FROM posts WHERE chat_id = $1 AND message_id = $2;',
                          int(call.message.chat.id), int(call.message.message_id)))['post_id']
        access_token = loop.run_until_complete(psql.fetchrow(
            'SELECT access_token FROM users WHERE id = $1;',
            int(owner_id)
        ))['access_token']

        post = requests.post("https://api.vk.com/method/wall.getById",
                             data={
                                 "posts": str(str(community_id) + "_" + str(post_id)),
                                 "copy_history_depth": 1,
                                 "extended": 1,
                                 "access_token": access_token,
                                 "v": "5.80"
                             }).json()['response']['items'][0]
        update_status = post_statistics(bot, posts=post, chat_id=call.message.chat.id,
                                       message_id=call.message.message_id, mtype="update")
        if update_status == "OK" or update_status == "IS NOT MODIFIED":
            bot.answer_callback_query(callback_query_id=call.id,
                                      text="✅ Статистика данной публикации была успешно обновлена! "
                                           "Нажмите на кнопку(-и) еще раз, чтобы увидеть обновленные значения. "
                                           "Обратите внимание, что клиенту потребуется до 30 секунд для их обновления.",
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
            if call.data.startswith("channel_counters"):
                counter = call.data.split("|", 2)

                if counter[1] == "time":
                    bot.answer_callback_query(callback_query_id=call.id,
                                              text="🕒 Время публикации данного поста: {0} MSK.".format(
                                                  str(datetime.fromtimestamp(
                                                      int(counter[2])).strftime("%d.%m.%y, %H:%M:%S"))),
                                              show_alert=True, cache_time=30)
                elif counter[1] == "likes":
                    bot.answer_callback_query(callback_query_id=call.id,
                                              text="💖 Количество лайков: {0}.".format(
                                                  str(counter[2])), show_alert=True, cache_time=30)
                elif counter[1] == "comments":
                    bot.answer_callback_query(callback_query_id=call.id,
                                              text="💬 Количество комментариев: {0}.".format(
                                                  str(counter[2])), show_alert=True, cache_time=30)
                elif counter[1] == "reposts":
                    bot.answer_callback_query(callback_query_id=call.id,
                                              text="🔁 Количество репостов: {0}.".format(
                                                  str(counter[2])), show_alert=True, cache_time=30)
                elif counter[1] == "views":
                    bot.answer_callback_query(callback_query_id=call.id,
                                              text="👁 Количество просмотров: {0}.".format(
                                                  str(counter[2])), show_alert=True, cache_time=30)
                elif counter[1] == "poll":
                    poll = loop.run_until_complete(redis.execute("GET", str("poll&" + str(counter[2]))))
                    if not poll:
                        logging.debug("Poll Name is None, most likely this poll isn't in the cache.")
                        refresh_stats(bot, call, expired=1)
                        return
                    bot.answer_callback_query(callback_query_id=call.id,
                                              text="📋 Название голосования: {0}.".format(
                                                  str(poll[0:170])), show_alert=True, cache_time=30)
                elif counter[1] == "poll_ans":
                    poll_answer = loop.run_until_complete(redis.execute("GET", str("poll_answer&" + str(counter[2]))))
                    if not poll_answer:
                        logging.debug("Poll Answer is None, most likely this poll isn't in the cache.")
                        refresh_stats(bot, call, expired=1)
                        return
                    else:
                        poll_answer = poll_answer.split("?|&|&|!", 1)
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

# -*- coding: utf-8 -*-

from app import logging
from app.bot import bot as bot
from app.remote.redis import Redis as redis
from telebot import types
from telebot import apihelper
from datetime import datetime
from ast import literal_eval
from math import ceil
import logging
import asyncio


def statistics(posts, chat_id, mtype="initiate", message_id=None):
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        poll = None

        try:
            try:
                # noinspection PyStatementEffect
                posts['attachments']

                poll = []

                for anum in range(len(posts['attachments'])):
                    if posts['attachments'][anum]['type'] == "poll":
                        poll.extend([{"question": str(posts['attachments'][anum]['poll']['question']),
                                      "answers": literal_eval(
                                          str(posts['attachments'][anum]['poll']['answers']))}])
            except KeyError:
                logging.debug("There is no attachments in this post: " + str(posts['owner_id']) +
                              "_" + str(posts['id']) + ".")
        except Exception as e:
            logging.error("Exception has been occurred while trying to execute the method.", exc_info=True)

        markup = types.InlineKeyboardMarkup()
        markup.row(
            types.InlineKeyboardButton("🕒 {0}".format(
                str(datetime.fromtimestamp(int(posts['date'])).strftime("%H:%M"))),
                callback_data="channel_counters_time|{0}_{1}_{2}|{3}".format(
                    str(chat_id), str(posts['owner_id']),
                    str(posts['id']), str(posts['date']))))
        markup.row(
            types.InlineKeyboardButton("💖 {0}".format(
                (str(ceil(int(posts['likes']['count']) / 1000.0) * 1) + "K" if int(posts['likes']['count']) > 1000
                 else str(posts['likes']['count']))),
                callback_data="channel_counters_likes|{0}_{1}_{2}|{3}".format(
                    str(chat_id), str(posts['owner_id']),
                    str(posts['id']), str(posts['likes']['count']))),
            types.InlineKeyboardButton("💬 {0}".format(
                (str(ceil(int(posts['comments']['count']) / 1000.0) * 1) + "K" if int(posts['comments']['count']) > 1000
                 else str(posts['comments']['count']))),
                callback_data="channel_counters_comments|{0}_{1}_{2}|{3}".format(
                    str(chat_id), str(posts['owner_id']),
                    str(posts['id']), str(posts['comments']['count']))),
            types.InlineKeyboardButton("🔁 {0}".format(
                (str(ceil(int(posts['reposts']['count']) / 1000.0) * 1) + "K" if int(posts['reposts']['count']) > 1000
                 else str(posts['reposts']['count']))),
                callback_data="channel_counters_reposts|{0}_{1}_{2}|{3}".format(
                    str(chat_id), str(posts['owner_id']),
                    str(posts['id']), str(posts['reposts']['count']))),
            types.InlineKeyboardButton("👁️ {0}".format(
                (str(ceil(int(posts['views']['count']) / 1000.0) * 1) + "K" if int(posts['views']['count']) > 1000
                 else str(posts['views']['count']))),
                callback_data="channel_counters_views|{0}_{1}_{2}|{3}".format(
                    str(chat_id), str(posts['owner_id']),
                    str(posts['id']), str(posts['views']['count']))))

        if poll:
            markup.row(
                types.InlineKeyboardButton("📋 {0}".format(
                    str(poll[0]['question'])),
                    callback_data="channel_polls"))
            for pint in range(len(poll[0]['answers'])):
                poll[0]['answers'][0]['votes'] = 134823
                poll[0]['answers'][1]['votes'] = 98032
                # noinspection PyTypeChecker
                markup.row(
                    types.InlineKeyboardButton("❎ {0} — {1} голосов".format(
                        str(poll[0]['answers'][pint]['text']),
                        (str(ceil(int(poll[0]['answers'][pint]['votes']) / 1000.0) * 1) + "K" if int(
                            poll[0]['answers'][pint]['votes']) > 1000
                         else str(poll[0]['answers'][pint]['votes']))),
                        callback_data="channel_counters_poll_answers|{0}_{1}_{2}|{3}".format(
                            str(chat_id), str(posts['owner_id']),
                            str(posts['id']), str(poll[0]['answers'][pint]['votes']))))

        markup.row(
            types.InlineKeyboardButton("🔄 Обновить статистику",
                                       callback_data="channel_refresh_counters|{0}_{1}_{2}".format(
                                           str(chat_id), str(posts['owner_id']),
                                           str(posts['id'])))
        )

        loop.run_until_complete(redis.execute("SET", "channel_counters|{0}_{1}_{2}".format(
            str(chat_id), str(posts['owner_id']), str(posts['id'])
        ), "OK"))
        loop.run_until_complete(redis.execute("EXPIRE", "channel_counters|{0}_{1}_{2}".format(
            str(chat_id), str(posts['owner_id']), str(posts['id'])
        ), "300"))

        if mtype == "initiate":
            return markup, poll
        elif mtype == "update":
            try:
                bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id, reply_markup=markup)
                return "OK"
            except apihelper.ApiException as e:
                if "Bad Request: message is not modified" in str(e):
                    return "IS NOT MODIFIED"
                else:
                    return "ERROR"
    except Exception as e:
        logging.error("Exception has been occurred while trying to execute the method.", exc_info=True)
        return e

# -*- coding: utf-8 -*-

from app import logging
from app.remote.redis import Redis as redis
from telegram.ext import run_async
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import BadRequest
from datetime import datetime
from uuid import uuid4
from ast import literal_eval
from time import time
from math import ceil
import logging
import asyncio


# @run_async
# noinspection PyTypeChecker,PyStatementEffect
def statistics(bot, posts, chat_id, mtype="initiate", message_id=None):
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        poll = None

        try:
            try:
                posts['attachments']

                poll = []

                for anum in range(len(posts['attachments'])):
                    if posts['attachments'][anum]['type'] == "poll":
                        poll.extend([{"question": str(posts['attachments'][anum]['poll']['question']),
                                      "answers": literal_eval(
                                          str(posts['attachments'][anum]['poll']['answers']))}])
            except KeyError:
                logging.debug("KeyError Exception has been occurred, most likely the post doesn't have "
                              "any attachments.", exc_info=True)
        except Exception as e:
            logging.error("Exception has been occurred while trying to execute the method.", exc_info=True)

        for elm in ["time", "likes", "comments", "reposts", "views"]:
            if elm is "time":
                pass
            else:
                try:
                    posts[elm]['count']
                except KeyError:
                    posts[elm] = {"count": 0}

        markup = []

        markup.extend([
            [InlineKeyboardButton("🕒 {0}".format(
                str(datetime.fromtimestamp(int(posts['date'])).strftime("%H:%M"))),
                callback_data="channel_counters|time|{0}".format(str(posts['date'])))]
        ])
        markup.extend([[
            InlineKeyboardButton("💖 {0}".format(
                (str(ceil(int(posts['likes']['count']) / 1000.0) * 1) + "K" if int(posts['likes']['count']) > 1000
                 else str(posts['likes']['count']))),
                callback_data="channel_counters|likes|{0}".format(str(posts['likes']['count']))),
            InlineKeyboardButton("💬 {0}".format(
                (str(ceil(int(posts['comments']['count']) / 1000.0) * 1) + "K" if int(posts['comments']['count']) > 1000
                 else str(posts['comments']['count']))),
                callback_data="channel_counters|comments|{0}".format(str(posts['comments']['count']))),
            InlineKeyboardButton("🔁 {0}".format(
                (str(ceil(int(posts['reposts']['count']) / 1000.0) * 1) + "K" if int(posts['reposts']['count']) > 1000
                 else str(posts['reposts']['count']))),
                callback_data="channel_counters|reposts|{0}".format(str(posts['reposts']['count']))),
            InlineKeyboardButton("👁️ {0}".format(
                (str(ceil(int(posts['views']['count']) / 1000.0) * 1) + "K" if int(posts['views']['count']) > 1000
                 else str(posts['views']['count']))),
                callback_data="channel_counters|views|{0}".format(str(posts['views']['count']))),
        ]])

        if poll:
            poll_uuid = uuid4()
            try:
                poll[0]['question'][31]
                poll_question = str(poll[0]['question'][0:30]) + "..."
            except IndexError:
                poll_question = str(poll[0]['question'][0:30])

            markup.extend([
                [InlineKeyboardButton("📋 {0}".format(
                    str(poll_question)),
                    callback_data="channel_counters|poll|{0}".format(str(poll_uuid)))]])
            loop.run_until_complete(redis.execute("SET", str("poll&" + str(poll_uuid)), str(poll[0]['question'])))
            logging.debug("Poll UUID: " + str(poll_uuid))

            for pint in range(len(poll[0]['answers'])):
                pollanswer_uuid = uuid4()
                try:
                    poll[0]['answers'][pint]['text'][31]
                    poll_question = str(poll[0]['answers'][pint]['text'][0:30]) + "..."
                except IndexError:
                    poll_question = str(poll[0]['answers'][pint]['text'][0:30])

                markup.extend([[
                    InlineKeyboardButton("❎ {0} — {1} 👍🏻".format(
                        str(poll_question),
                        (str(ceil(int(poll[0]['answers'][pint]['votes']) / 1000.0) * 1) + "K" if int(
                            poll[0]['answers'][pint]['votes']) > 1000
                         else str(poll[0]['answers'][pint]['votes']))),
                        callback_data="channel_counters|poll_ans|{0}".format(
                            str(pollanswer_uuid)))]])
                loop.run_until_complete(redis.execute("SET", str("poll_answer&" + str(pollanswer_uuid)), str(
                    str(poll[0]['answers'][pint]['text']) + "&" + str(poll[0]['answers'][pint]['votes']))))
                logging.debug("Poll Answer UUID: " + str(pollanswer_uuid))

        markup.extend([
            [InlineKeyboardButton("🔄 Обновить статистику",
                                  callback_data="channel_refresh_stats|{0}&{1}|{2}".format(
                                      str(posts['owner_id']), str(posts['id']), str(int(int(time())) + 300)))]])

        markup = InlineKeyboardMarkup(markup)

        if mtype == "initiate":
            return markup
        elif mtype == "update":
            try:
                bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id, reply_markup=markup)
                return "OK"
            except BadRequest as e:
                if "Message is not modified" in str(e):
                    return "IS NOT MODIFIED"
                else:
                    logging.error("Exception BadRequest has been occurred while trying to edit message markup.",
                                  exc_info=True)
                    return "ERROR"
    except Exception as e:
        logging.error("Exception has been occurred while trying to execute the method.", exc_info=True)
        return e

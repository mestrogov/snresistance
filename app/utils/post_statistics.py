# -*- coding: utf-8 -*-

from app import logging
from telegram.ext import run_async
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import BadRequest
from datetime import datetime
from time import time
from math import ceil
import logging
import asyncio


# @run_async
def statistics(bot, posts, chat_id, mtype="initiate", message_id=None):
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        poll = None

        # TODO: Rewrite polls code
        """
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
        """

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

        # TODO: Rewrite polls code
        """
        if poll:
            markup.extend([
                [InlineKeyboardButton("📋 {0}".format(
                    str(poll[0]['question'])),
                    callback_data="channel_polls")]
            ])
            for pint in range(len(poll[0]['answers'])):
                # noinspection PyTypeChecker
                markup.extend([[
                    InlineKeyboardButton("❎ {0} — {1} 👍🏻".format(
                        str(poll[0]['answers'][pint]['text']),
                        (str(ceil(int(poll[0]['answers'][pint]['votes']) / 1000.0) * 1) + "K" if int(
                            poll[0]['answers'][pint]['votes']) > 1000
                         else str(poll[0]['answers'][pint]['votes']))),
                        callback_data="channel_counters_poll_answers|{0}_{1}_{2}|{3}".format(
                            str(chat_id), str(posts['owner_id']),
                            str(posts['id']), str(poll[0]['answers'][pint]['votes'])))]])
        """

        markup.extend([
            [InlineKeyboardButton("🔄 Обновить статистику",
                                  callback_data="channel_refresh_stats|{0}&{1}|{2}".format(
                                      str(posts['owner_id']), str(posts['id']), str(int(int(time())) + 300)))]])

        markup = InlineKeyboardMarkup(markup)

        if mtype == "initiate":
            return markup, poll
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

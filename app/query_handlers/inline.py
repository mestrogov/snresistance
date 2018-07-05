# -*- coding: utf-8 -*-

from app import logging
from app import config as config
from app.remote.postgresql import Psql as psql
from app.remote.redis import Redis as redis
from telegram.ext.dispatcher import run_async
from telegram import InlineQueryResultArticle, InputTextMessageContent
from uuid import uuid4
import logging
import asyncio
import requests


@run_async
def inline_query(bot, query):
    query = query.inline_query
    if str(query.query).startswith("Initialize Channel: #"):
        community = str(query.query).replace("Initialize Channel: #", "")
    else:
        results = [
            InlineQueryResultArticle(
                id=uuid4(),
                title="Отправить информацию обо мне в этот чат.",
                input_message_content=InputTextMessageContent(
                    (config.startMessage + "\n\n[Отказаться от социальных сетей: @SNResistanceBot]"
                                           "(https://t.me/SNResistanceBot?start=inline_query_share)"),
                    parse_mode="Markdown"))]

        bot.answer_inline_query(query.id, results=results,
                                switch_pm_text="Подробнее о моих возможностях.",
                                switch_pm_parameter="start_inline_query_command")

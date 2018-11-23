# -*- coding: utf-8 -*-


from app import logging
from app.remote.redis import Redis as redis
from telegram.ext.dispatcher import run_async
import logging
import asyncio
import json


@run_async
def message(bot, message):
    try:
        message = message.message
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        if not message.text.startswith("/"):
            status = loop.run_until_complete(redis.execute("GET", "status:{0}".format(message.from_user.id)))
            if status:
                status = json.loads(str(status))
                if status['method'] == "find_communities":
                    # TODO: Add here find_communities method to find community in DB if it exists
                    bot.send_message(message.from_user.id, "Все огонь!")
                    loop.run_until_complete(redis.execute("DEL", "status:{0}".format(message.from_user.id)))
    except Exception as e:
        logging.error("Exception has been occurred while trying to execute the method.", exc_info=True)
        return e

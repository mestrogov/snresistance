# -*- coding: utf-8 -*-


from app import logging
from app import config as config
from app.channels.polling import polling as channel_polling
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram import Bot
from app.commands.start import start as start
from app.commands.cancel import cancel as cancel
from app.commands.debug import debug as debug_command
from app.commands.communities import add_community as add_community
from app.commands.communities import remove_community as remove_community
from app.handlers.message import message as message_handler
from app.handlers.callback import callback as callback_query
import logging


def bot_initialize():
    try:
        bot_updater = Updater(config.botToken, workers=16)
        dp = bot_updater.dispatcher
        jq = bot_updater.job_queue

        dp.add_handler(CommandHandler("start", start))
        dp.add_handler(CommandHandler("cancel", cancel))
        dp.add_handler(CommandHandler("debug", debug_command))
        dp.add_handler(CommandHandler("addcommunity", add_community))
        dp.add_handler(CommandHandler("removecommunity", remove_community))
        dp.add_handler(MessageHandler(Filters.text, message_handler))
        dp.add_handler(CallbackQueryHandler(callback_query))
        dp.add_error_handler(error_handler)

        jq.run_repeating(channel_polling, interval=900, first=5)

        bot_updater.start_polling(clean=True, timeout=15, read_latency=20)

        return bot_updater
    except Exception as e:
        logging.critical("Exception has been occurred while trying to set up bot settings.", exc_info=True)
        return e


def bot_configuration():
    try:
        bot = Bot(config.botToken)

        return bot
    except Exception as e:
        logging.critical("Exception has been occurred while trying to set up bot settings.", exc_info=True)
        return e


def error_handler(bot, update, error):
    logging.error("Exception has been occurred while trying to execute update {0}. Error: {1}.".format(
        str(update), str(error)
    ))

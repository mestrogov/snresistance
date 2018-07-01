# -*- coding: utf-8 -*-

from app import logging
from app.bot import bot as bot
from app import callback as callback
from app.commands import channel as channel
from app.commands import communities as communities
from app.commands import debug as debug
from app.commands import start as start
from threading import Thread
from threading import enumerate
import logging


# noinspection PyTypeChecker,PyUnboundLocalVariable
@bot.callback_query_handler(func=lambda call: True)
def callback_query_handler(call):
    try:
        logging.debug("Passed argument: " + str(call))

        thread = Thread(target=callback.callback_query, args=(call,))
        thread.setDaemon(True)
        thread.start()

        logging.debug("All threads which are running now: " + str(enumerate()))
    except Exception as e:
        logging.error("Exception has been occurred while trying to execute the method.", exc_info=True)
        return e


@bot.message_handler(commands=['start'])
def command_start_handler(message):
    try:
        logging.debug("Passed argument: " + str(message))

        thread = Thread(target=start.start, args=(message,))
        thread.setDaemon(True)
        thread.start()

        logging.debug("All threads which are running now: " + str(enumerate()))
    except Exception as e:
        logging.error("Exception has been occurred while trying to execute the method.", exc_info=True)
        return e


# noinspection PyTypeChecker
@bot.message_handler(commands=['debug'])
def command_debug_handler(message):
    try:
        logging.debug("Passed argument: " + str(message))

        thread = Thread(target=debug.debug, args=(message,))
        thread.setDaemon(True)
        thread.start()

        logging.debug("All threads which are running now: " + str(enumerate()))
    except Exception as e:
        logging.error("Exception has been occurred while trying to execute the method.", exc_info=True)
        return e


# noinspection PyTypeChecker
@bot.message_handler(commands=['add', 'subscribe', 'sub'])
def command_add_handler(message):
    try:
        logging.debug("Passed argument: " + str(message))

        thread = Thread(target=communities.addcommunity, args=(message,))
        thread.setDaemon(True)
        thread.start()

        logging.debug("All threads which are running now: " + str(enumerate()))
    except Exception as e:
        logging.error("Exception has been occurred while trying to execute the method.", exc_info=True)
        return e


# noinspection PyTypeChecker
@bot.message_handler(commands=['remove', 'unsubscribe', 'unsub'])
def command_remove_handler(message):
    try:
        logging.debug("Passed argument: " + str(message))

        thread = Thread(target=communities.removecommunity, args=(message,))
        thread.setDaemon(True)
        thread.start()

        logging.debug("All threads which are running now: " + str(enumerate()))
    except Exception as e:
        logging.error("Exception has been occurred while trying to execute the method.", exc_info=True)
        return e


# noinspection PyTypeChecker
@bot.message_handler(commands=['addchannel'])
def command_addchannel_handler(message):
    try:
        logging.debug("Passed argument: " + str(message))

        thread = Thread(target=channel.addchannel, args=(message,))
        thread.setDaemon(True)
        thread.start()

        logging.debug("All threads which are running now: " + str(enumerate()))
    except Exception as e:
        logging.error("Exception has been occurred while trying to execute the method.", exc_info=True)
        return e


@bot.channel_post_handler()
def command_initiatechannel_handler(message):
    try:
        logging.debug("Passed argument: " + str(message))

        thread = Thread(target=channel.initiatechannel, args=(message,))
        thread.setDaemon(True)
        thread.start()

        logging.debug("All threads which are running now: " + str(enumerate()))
    except Exception as e:
        logging.error("Exception has been occurred while trying to execute the method.", exc_info=True)
        return e

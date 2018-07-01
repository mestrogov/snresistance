# -*- coding: utf-8 -*-


from app import logging
from app import config as config
import logging
import telebot


try:
    global bot
    # noinspection PyRedeclaration
    bot = telebot.TeleBot(config.botToken)
except Exception as e:
    logging.critical("Exception has been occurred while trying to set up bot settings.", exc_info=True)
    raise Exception

# -*- coding: utf-8 -*-

import requests
import shutil
import secrets
import os
# noinspection PyPackageRequirements
import telebot
# noinspection PyPackageRequirements
from telebot import types
# noinspection PyPackageRequirements,PyUnresolvedReferences
import config as config
import time
import datetime
import calendar
import threading
import asyncio
import asyncpg
import aioredis
import ast
import re
import logging
from operator import itemgetter


try:
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    logging.addLevelName(logging.DEBUG, '\x1b[32m%s\x1b[0m' % logging.getLevelName(logging.DEBUG))
    logging.addLevelName(logging.INFO, '\x1b[34m%s\x1b[0m' % logging.getLevelName(logging.INFO))
    logging.addLevelName(logging.WARNING, '\x1b[33m%s\x1b[0m' % logging.getLevelName(logging.WARNING))
    logging.addLevelName(logging.ERROR, '\x1b[31m%s\x1b[0m' % logging.getLevelName(logging.ERROR))
    logging.addLevelName(logging.CRITICAL, '\x1b[31;1m%s\x1b[0m' % logging.getLevelName(logging.CRITICAL))

    if config.developerMode:
        formatter = logging.Formatter('%(threadName)s/%(filename)s:%(lineno)d/%(funcName)s() | %(asctime)s | '
                                      '%(levelname)s  >  %(message)s', '%d.%m.%y, %H:%M:%S')
    else:
        formatter = logging.Formatter('%(asctime)s | %(levelname)s  >  %(message)s',
                                      '%d.%m.%y, %H:%M:%S')

    fileHandler = logging.FileHandler("latest.log")
    fileHandler.setLevel(logging.INFO)
    fileHandler.setFormatter(formatter)
    logger.addHandler(fileHandler)

    consoleHandler = logging.StreamHandler()
    if config.developerMode:
        consoleHandler.setLevel(logging.DEBUG)
    else:
        consoleHandler.setLevel(logging.INFO)
    consoleHandler.setFormatter(formatter)
    logger.addHandler(consoleHandler)

    if config.developerMode:
        ignoredModulesLoggers = []
        # noinspection PyUnresolvedReferences
        for logger in logging.Logger.manager.loggerDict:
            ignoredModulesLoggers.extend([logger])
            logging.getLogger(logger).setLevel(logging.WARNING)
        logging.debug("Ignoring these Modules' Loggers: " + str(ignoredModulesLoggers) + '.')
except:
    logging.critical("Exception has been occurred while trying to set up logging settings.", exc_info=True)


try:
    bot = telebot.TeleBot(config.botToken)

    botVKSentErrorMessage = None
    sentPosts = []
except:
    logging.critical("Exception has been occurred while trying to set up bot settings.", exc_info=True)


# noinspection PyPep8Naming
class PSQL:
    @staticmethod
    async def connection():
        try:
            response = await PSQL.fetchrow("SELECT pong FROM ping WHERE pong = TRUE;")

            logging.info("The connection to the PostgreSQL can be established successfully.")
            logging.debug("Returned response: " + str(response))

            return "OK"
        except Exception as e:
            logging.error("Exception has been occurred while trying to establish connection to "
                          "PostgreSQL.", exc_info=True)
            return e

    @classmethod
    async def execute(cls, *args):
        try:
            logging.debug("Passed arguments: " + str(args))

            psql_connection = await asyncpg.connect(host=config.databaseHost,
                                                    database=config.databaseName,
                                                    user=config.databaseUsername,
                                                    port=config.databasePort)

            await psql_connection.execute(*args)
            await psql_connection.close()
            return "OK"
        except Exception as e:
            logging.error("Exception has been occurred while trying to execute SQL statement.", exc_info=True)
            return e

    @classmethod
    async def fetch(cls, *args):
        try:
            logging.debug("Passed arguments: " + str(args))

            psql_connection = await asyncpg.connect(host=config.databaseHost,
                                                    database=config.databaseName,
                                                    user=config.databaseUsername,
                                                    port=config.databasePort)

            result = await psql_connection.fetch(*args)
            await psql_connection.close()
            # The result can be parsed by using: result[0]['COLUMN']
            return result
        except Exception as e:
            logging.error("Exception has been occurred while trying to fetch data from PostgreSQL.", exc_info=True)
            return e

    @classmethod
    async def fetchrow(cls, *args):
        try:
            logging.debug("Passed arguments: " + str(args))

            psql_connection = await asyncpg.connect(host=config.databaseHost,
                                                    database=config.databaseName,
                                                    user=config.databaseUsername,
                                                    port=config.databasePort)

            result = await psql_connection.fetchrow(*args)
            await psql_connection.close()
            return result
        except Exception as e:
            logging.error("Exception has been occurred while trying to fetch row of data "
                          "from PostgreSQL.", exc_info=True)
            return e


class Redis:
    @staticmethod
    async def connection():
        try:
            response = await Redis.execute("ping")

            logging.info("The connection to Redis Server can be established successfully.")
            logging.debug("Returned response: " + str(response))
            return "OK"
        except Exception as e:
            logging.error("Exception has been occurred while trying to establish connection with "
                          "Redis.", exc_info=True)
            return e

    @classmethod
    async def execute(cls, *args):
        try:
            logging.debug("Passed arguments: " + str(args))

            redis_connection = await aioredis.create_connection(
                (config.redisHost, config.redisPort), encoding="UTF-8")

            result = await redis_connection.execute(*args, encoding="UTF-8")
            redis_connection.close()
            await redis_connection.wait_closed()
            return result
        except Exception as e:
            logging.error("Exception has been occurred while trying to execute Redis statement.", exc_info=True)
            return e


# noinspection PyTypeChecker,PyUnboundLocalVariable
@bot.callback_query_handler(func=lambda call: True)
def callback_query_handler(call):
    try:
        logging.debug("Passed argument: " + str(call))

        thread = threading.Thread(target=callback_query, args=(call,))
        thread.setDaemon(True)
        thread.start()

        logging.debug("Thread " + str(thread) + " has been started.")
    except Exception as e:
        logging.error("Exception has been occurred while trying to execute the method.", exc_info=True)
        return e


def callback_query(call):
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        if call.message:
            if call.data == "exit_to_start_menu":
                bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
                menu_start(message=call)
            if call.data == "start_vk_import":
                markup = types.InlineKeyboardMarkup(row_width=1)
                markup.add(
                    types.InlineKeyboardButton("Импортировать", url="google.com"),
                    types.InlineKeyboardButton("❌  Отменить", callback_data="exit_to_start_menu")
                )
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
                logging.warning("The temporary stub for callback with start_menu_next data.")
            elif call.data.startswith("channel_counters_"):
                data_splitted = call.data.replace("channel_counters_", "", 1).split("|")

                cached = loop.run_until_complete(
                    Redis.execute("EXISTS", "channel_counters|{0}".format(str(data_splitted[1]))))
                cached = int(cached)
                if cached:
                    counters_data_splitted = loop.run_until_complete(Redis.execute("GET", "channel_counters|{0}".format(
                        str(data_splitted[1])
                    ))).split("_")
                else:
                    owner_id = loop.run_until_complete(PSQL.fetchrow('SELECT owner_id FROM channels WHERE id = $1;',
                                                                     int(call.message.json['chat']['id'])))['owner_id']
                    token = loop.run_until_complete(PSQL.fetchrow(
                        'SELECT vk_token FROM users WHERE id = $1;',
                        int(owner_id)
                    ))['vk_token']

                    ids_data_splitted = data_splitted[1].split("_")
                    post_counters = requests.post("https://api.vk.com/method/wall.getById",
                                                  data={
                                                      "posts": str(
                                                          str(ids_data_splitted[1]) + "_" +
                                                          str(ids_data_splitted[2])
                                                      ),
                                                      "copy_history_depth": 1,
                                                      "extended": 1,
                                                      "access_token": token,
                                                      "v": "5.78"
                                                  }).json()['response']['items'][0]
                    counters_data_splitted = "{0}_{1}_{2}_{3}_{4}".format(
                        str(post_counters['date']),
                        str(post_counters['likes']['count']),
                        str(post_counters['comments']['count']),
                        str(post_counters['reposts']['count']),
                        str(post_counters['views']['count'])
                    ).split("_")

                if data_splitted[0] == "time":
                    bot.answer_callback_query(callback_query_id=call.id,
                                              text="🕒 Время публикации данного поста: {0} MSK.".format(
                                                  str(datetime.datetime.fromtimestamp(
                                                      int(counters_data_splitted[0])).strftime("%H:%M"))),
                                              show_alert=True)
                elif data_splitted[0] == "likes":
                    bot.answer_callback_query(callback_query_id=call.id,
                                              text="💖 Общее количество лайков: {0}.".format(
                                                  str(counters_data_splitted[1]), show_alert=True))
                elif data_splitted[0] == "comments":
                    bot.answer_callback_query(callback_query_id=call.id,
                                              text="💬 Общее количество комментариев: {0}.".format(
                                                  str(counters_data_splitted[2]), show_alert=True))
                elif data_splitted[0] == "reposts":
                    bot.answer_callback_query(callback_query_id=call.id,
                                              text="🔁 Общее количество репостов: {0}.".format(
                                                  str(counters_data_splitted[3]), show_alert=True))
                elif data_splitted[0] == "views":
                    bot.answer_callback_query(callback_query_id=call.id,
                                              text="👁 Общее количество просмотров: {0}.".format(
                                                  str(counters_data_splitted[4]), show_alert=True))
                else:
                    bot.answer_callback_query(callback_query_id=call.id,
                                              text="❗ Ой, что-то пошло не так. Попробуйте через некоторое время.",
                                              show_alert=True)

            bot.answer_callback_query(callback_query_id=call.id, show_alert=False)
    except Exception as e:
        try:
            bot.send_message(call.from_user.id,
                             "❗ *Извините, что-то пошло не так, но в скором времени все исправится. "
                             "Попробуйте выполнить то же самое действие через некоторое время (10-15 минут).*",
                             parse_mode="Markdown")
        except:
            pass

        logging.error("Exception has been occurred while trying to execute the method.", exc_info=True)
        return e


# noinspection PyTypeChecker
@bot.message_handler(commands=['start'])
def command_start_handler(message):
    try:
        logging.debug("Passed argument: " + str(message))

        thread = threading.Thread(target=command_start, args=(message,))
        thread.setDaemon(True)
        thread.start()

        logging.debug("Thread " + str(thread) + " has been started.")
    except Exception as e:
        logging.error("Exception has been occurred while trying to execute the method.", exc_info=True)
        return e


def command_start(message):
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        if "ru" not in message.from_user.language_code:
            bot.send_message(message.from_user.id,
                             "❗ *Unfortunately, the bot doesn't speak your language. So if you are "
                             "not able to understand the text that is written below, use an online translator "
                             "such as Google Translate.*",
                             parse_mode="Markdown")

        bot.send_message(message.from_user.id, config.startMessage, parse_mode="Markdown")
        menu_start(message)

        loop.run_until_complete(PSQL.execute(
            'INSERT INTO users("id") VALUES($1) RETURNING "id", "is_paid", "vk_token", "communities";',
            message.from_user.id
        ))
    except Exception as e:
        try:
            bot.send_message(message.from_user.id,
                             "❗ *Извините, что-то пошло не так, но в скором времени все исправится. "
                             "Попробуйте выполнить то же самое действие через некоторое время (10-15 минут).*",
                             parse_mode="Markdown")
        except:
            pass

        logging.error("Exception has been occurred while trying to execute the method.", exc_info=True)
        return e


def menu_start(message):
    try:
        logging.debug("Passed argument: " + str(message))

        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton("Импортировать все мои сообщества", callback_data="start_vk_import"),
            types.InlineKeyboardButton("Указать прямую ссылку на сообщество", callback_data="start_menu_direct_url")
            )
        bot.send_message(message.from_user.id,
                         "Выберите способ, с помощью которого Вы хотите подписаться на первое сообщество ВКонтакте, "
                         "используя мои возможности.",
                         reply_markup=markup)
    except Exception as e:
        try:
            bot.send_message(message.from_user.id,
                             "❗ *Извините, что-то пошло не так, но в скором времени все исправится. "
                             "Попробуйте выполнить то же самое действие через некоторое время (10-15 минут).*",
                             parse_mode="Markdown")
        except:
            pass

        logging.error("Exception has been occurred while trying to execute the method.", exc_info=True)
        return e


# noinspection PyTypeChecker
@bot.message_handler(commands=['debug'])
def command_debug_handler(message):
    try:
        logging.debug("Passed argument: " + str(message))

        thread = threading.Thread(target=command_debug, args=(message,))
        thread.setDaemon(True)
        thread.start()

        logging.debug("Thread " + str(thread) + " has been started.")
    except Exception as e:
        logging.error("Exception has been occurred while trying to execute the method.", exc_info=True)
        return e


def command_debug(message):
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        is_paid = loop.run_until_complete(PSQL.fetchrow(
            'SELECT is_paid FROM users WHERE id = $1;',
            message.from_user.id
        ))['is_paid']
        communities = loop.run_until_complete(PSQL.fetchrow(
            'SELECT communities FROM users WHERE id = $1;',
            message.from_user.id
        ))['communities']

        bot.send_message(message.from_user.id,
                         "Вот информация, которая может помочь людям с хорошими намерениями."
                         "\n\n*Не скидывайте ее тому, кому не доверяете, хотя здесь фактически нет конфиденциальной "
                         "информации, но зачем предоставлять лишнюю информацию людям?*"
                         "\n\n*Global:*"
                         "\nUser ID: `{0}`"
                         "\nMessage ID: `{1}`"
                         "\nLanguage Code: `{2}`"
                         "\n\n*Database:*"
                         "\nIs Paid: `{3}`"
                         "\nCommunities: `{4}`".format(
                            str(message.from_user.id), str(message.message_id),
                            str(message.from_user.language_code), str(is_paid), str(communities)
                         ), parse_mode="Markdown")
    except Exception as e:
        try:
            bot.send_message(message.from_user.id,
                             "❗ *Извините, что-то пошло не так, но в скором времени все будет исправлено. "
                             "Попробуйте выполнить то же самое действие через некоторое время (10-15 минут).*",
                             parse_mode="Markdown")
        except:
            pass

        logging.error("Exception has been occurred while trying to execute the method.", exc_info=True)
        return e


# noinspection PyTypeChecker
@bot.message_handler(commands=['add', 'subscribe', 'sub'])
def command_add_handler(message):
    try:
        logging.debug("Passed argument: " + str(message))

        thread = threading.Thread(target=command_add, args=(message,))
        thread.setDaemon(True)
        thread.start()

        logging.debug("Thread " + str(thread) + " has been started.")
    except Exception as e:
        logging.error("Exception has been occurred while trying to execute the method.", exc_info=True)
        return e


def command_add(message):
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        communities = []
        communities_old = loop.run_until_complete(PSQL.fetchrow(
            'SELECT communities FROM users WHERE id = $1;',
            message.from_user.id
        ))['communities']
        # print(communities_old)
        if communities_old:
            communities_old = ast.literal_eval(communities_old)
            for elm in communities_old:
                communities.extend([elm])

        try:
            cm_url = message.text.split('vk.com/')[1]

            if cm_url in communities:
                bot.send_message(message.from_user.id,
                                 "В Ваших подписках уже есть такое сообщество, добавьте другое.")
            else:
                bot.send_message(message.from_user.id,
                                 "Вы успешно добавили новое сообщество в подписки! Надеюсь, оно хорошее (:")

                communities.extend([cm_url])
                loop.run_until_complete(PSQL.execute(
                    'UPDATE users SET "communities"=$1 WHERE "id"=$2 RETURNING "id", "is_paid", "vk_token", '
                    '"communities";',
                    str(communities), message.from_user.id
                ))
        except Exception:
            bot.send_message(message.from_user.id,
                             "Упс! Похоже, что Вы указали ссылку в неправильном формате. "
                             "Пример правильной команды: `vk.com/examplecommunity`", parse_mode="Markdown")
    except Exception as e:
        try:
            bot.send_message(message.from_user.id,
                             "❗ *Извините, что-то пошло не так, но в скором времени все будет исправлено. "
                             "Попробуйте выполнить то же самое действие через некоторое время (10-15 минут).*",
                             parse_mode="Markdown")
        except:
            pass

        logging.error("Exception has been occurred while trying to execute the method.", exc_info=True)
        return e


# noinspection PyTypeChecker
@bot.message_handler(commands=['remove', 'unsubscribe', 'unsub'])
def command_remove_handler(message):
    try:
        logging.debug("Passed argument: " + str(message))

        thread = threading.Thread(target=command_remove, args=(message,))
        thread.setDaemon(True)
        thread.start()

        logging.debug("Thread " + str(thread) + " has been started.")
    except Exception as e:
        logging.error("Exception has been occurred while trying to execute the method.", exc_info=True)
        return e


def command_remove(message):
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        communities = []
        communities_db = loop.run_until_complete(PSQL.fetchrow(
            'SELECT communities FROM users WHERE id = $1;',
            message.from_user.id
        ))['communities']
        # print(communities_db)
        if communities_db:
            communities_db = ast.literal_eval(communities_db)
            for elm in communities_db:
                communities.extend([elm])

        try:
            cm_url = message.text.split('vk.com/')[1]

            if cm_url not in communities:
                bot.send_message(message.from_user.id,
                                 "В Ваших подписках нет такого сообщества.")
            else:
                bot.send_message(message.from_user.id,
                                 "Вы успешно отписались от сообщества!")

                communities.remove(cm_url)
                loop.run_until_complete(PSQL.execute(
                    'UPDATE users SET "communities"=$1 WHERE "id"=$2 RETURNING "id", "is_paid", "vk_token", '
                    '"communities";',
                    str(communities), message.from_user.id
                ))
        except Exception:
            bot.send_message(message.from_user.id,
                             "Упс! Похоже, что Вы указали ссылку в неправильном формате. "
                             "Пример правильной команды: `vk.com/examplecommunity`", parse_mode="Markdown")
    except Exception as e:
        try:
            bot.send_message(message.from_user.id,
                             "❗ *Извините, что-то пошло не так, но в скором времени все будет исправлено. "
                             "Попробуйте выполнить то же самое действие через некоторое время (10-15 минут).*",
                             parse_mode="Markdown")
        except:
            pass

        logging.error("Exception has been occurred while trying to execute the method.", exc_info=True)
        return e


# noinspection PyTypeChecker
@bot.message_handler(commands=['addchannel'])
def command_addchannel_handler(message):
    try:
        logging.debug("Passed argument: " + str(message))

        thread = threading.Thread(target=command_addchannel, args=(message,))
        thread.setDaemon(True)
        thread.start()

        logging.debug("Thread " + str(thread) + " has been started.")
    except Exception as e:
        logging.error("Exception has been occurred while trying to execute the method.", exc_info=True)
        return e


def command_addchannel(message):
    try:
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton(text='Превратить канал',
                                       switch_inline_query="!initiateChannel 1243|1234"),
        )
        bot.send_message(message.from_user.id,
                         "Вы решили создать канал, добавьте меня в него и напишите команду: "
                         "`/initchannel@SNResistance {0}_id`",
                         parse_mode="Markdown", reply_markup=markup)
    except Exception as e:
        try:
            bot.send_message(message.from_user.id,
                             "❗ *Извините, что-то пошло не так, но в скором времени все будет исправлено. "
                             "Попробуйте выполнить то же самое действие через некоторое время (10-15 минут).*",
                             parse_mode="Markdown")
        except:
            pass

        logging.error("Exception has been occurred while trying to execute the method.", exc_info=True)
        return e


@bot.channel_post_handler()
def command_initiatechannel_handler(message):
    try:
        logging.debug("Passed argument: " + str(message))

        thread = threading.Thread(target=initiatechannel, args=(message,))
        thread.setDaemon(True)
        thread.start()

        logging.debug("Thread " + str(thread) + " has been started.")
    except Exception as e:
        logging.error("Exception has been occurred while trying to execute the method.", exc_info=True)
        return e


def initiatechannel(message):
    try:
        print("----------")
        print("Channel Name: " + str(message.chat.title))
        print("Channel ID: " + str(message.chat.id))

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        if "!initiateChannel" in message.text:
            command = message.text.replace("!initiateChannel", "").strip().split("|")
            if command[1].startswith("public"):
                command[1] = command[1].replace("public", "club", 1)

            user_id = int(command[0])
            user_vktoken = loop.run_until_complete(PSQL.fetchrow(
                'SELECT vk_token FROM users WHERE id = $1;',
                int(user_id)
            ))['vk_token']

            community = requests.post("https://api.vk.com/method/groups.getById",
                                      data={
                                          "group_id": str(command[1]),
                                          "fields": "description",
                                          "access_token": str(user_vktoken),
                                          "v": "5.78"
                                      }).json()['response'][0]

            channel_id = message.chat.id
            initiation_date = calendar.timegm(datetime.datetime.utcnow().utctimetuple())

            try:
                bot.set_chat_title(channel_id, community['name'])
            except:
                bot.send_message(user_id,
                                 "Не удалось изменить имя канала.")
                return

            try:
                lfile_name = str(secrets.token_hex(16)) + '.png'
                lfile_res = requests.get(community['photo_200'], stream=True)
                with open(lfile_name, 'wb') as lfile_out:
                    shutil.copyfileobj(lfile_res.raw, lfile_out)
                lphoto = open(lfile_name, 'rb')
                os.remove(lfile_name)
                bot.set_chat_photo(channel_id, lphoto)
            except:
                bot.send_message(user_id,
                                 "Не удалось установить логотип канала.")
                return

            try:
                pin_id = bot.send_message(channel_id, str(community['description']))
                bot.pin_chat_message(channel_id, pin_id.json['message_id'])
            except:
                pass
                """
                bot.send_message(user_id,
                                 "Не удалось отправить сообщение и закрепить его в канале.")
                return
                """

            try:
                bot.set_chat_description(channel_id, "Тестовое описание, чтобы проверить права Бота.")
            except:
                bot.send_message(user_id,
                                 "Не удалось изменить описание канала.")
                return

            bot.set_chat_description(channel_id, config.channelDescription)

            loop.run_until_complete(PSQL.execute(
                'INSERT INTO channels("id", "owner_id", "community_id", "initiation_date") '
                'VALUES($1, $2, $3, $4) RETURNING "id", "owner_id", "community_id", "initiation_date";',
                int(channel_id), int(user_id), int(community['id']), int(initiation_date)
             ))

            bot.send_message(int(user_id),
                             "Ваш канал успешно настроен и готов для получения новых постов.")
    except Exception as e:
        try:
            bot.send_message(message.from_user.id,
                             "❗ *Извините, что-то пошло не так, но в скором времени все будет исправлено. "
                             "Попробуйте выполнить то же самое действие через некоторое время (10-15 минут).*",
                             parse_mode="Markdown")
        except:
            pass

        logging.error("Exception has been occurred while trying to execute the method.", exc_info=True)
        return e


# noinspection PyPep8Naming
class channel:
    @classmethod
    def fix_markdown(cls, text):
        text = text + "*"
        regex_index = r'((([_*]).+?\3[^_*]*)*)([_*])'
        text = re.sub(regex_index, "\g<1>\\\\\g<4>", text)
        return channel.fix_markdown_urls(text)

    @classmethod
    def fix_markdown_urls(cls, text):
        regex_index = r'\[(.*?)\]\((.*?)\)'
        return re.sub(regex_index, '[\\1](\\2)', text)

    @staticmethod
    def Polling():
        while True:
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

                communities = loop.run_until_complete(PSQL.fetch(
                    'SELECT id, owner_id, community_id FROM channels;',
                ))

                time.sleep(1)

                for num in range(len(communities)):
                    vk_token = loop.run_until_complete(PSQL.fetchrow(
                        'SELECT vk_token FROM users WHERE id = $1;',
                        communities[num]['owner_id']
                    ))['vk_token']

                    posts = requests.post("https://api.vk.com/method/wall.get",
                                          data={
                                              "owner_id": str("-" + str(communities[num]['community_id'])),
                                              "count": 2,
                                              "filter": "all",
                                              "extended": 1,
                                              "access_token": vk_token,
                                              "v": "5.78"
                                          })

                    posts_original = posts.json()['response']
                    posts = posts.json()['response']['items']

                    for pnum in range(len(posts)):
                        is_posted = loop.run_until_complete(PSQL.fetchrow(
                            'SELECT post_id FROM posts WHERE chat_id = $1 AND community_id = $2 AND post_id = $3;',
                            int(communities[num]['id']), int(posts[pnum]['owner_id']), int(posts[pnum]['id'])
                        ))

                        if is_posted:
                            continue

                        try:
                            if str(posts[pnum]['marked_as_ads']) == "1":
                                continue
                        except:
                            pass

                        try:
                            if str(posts[pnum]['is_pinned']) == "1":
                                continue
                        except:
                            pass

                        if not config.developerMode:
                            loop.run_until_complete(PSQL.execute(
                                'INSERT INTO posts("chat_id", "community_id", "post_id") VALUES($1, $2, $3) '
                                'RETURNING "chat_id", "community_id", "post_id";',
                                int(communities[num]['id']), int(posts[pnum]['owner_id']), int(posts[pnum]['id'])
                            ))

                        """
                        # VK URL Parsing
                        post_text = posts['response']['items'][num]['text']
                        try:
                            post_text_part = post_text.partition('[')[-1].rpartition(']')[0]
                            post_text_splitted = post_text_part.split("|")
                            post_text_md = "[" + str(post_text_splitted[1]) + "]" + \
                                           "(https://vk.com/" + str(post_text_splitted[0]) + ")"
                            post_text = post_text.replace("[" + post_text_part + "]", post_text_md)
                        except:
                            pass

                        # Hashtags Removing
                        try:
                            post_text_stripping = post_text
                            text = {tag.strip("#") for tag in post_text_stripping.split() if tag.startswith("#")}
                            text = list(text)
                            for it in text:
                                _t = "#" + it
                                post_text = post_text.replace(_t, "")
                        except:
                            pass
                        
                        "\n\n\n❗️К данной публикации что-то прикреплено, "
                                         "[перейдите на этот пост во ВКонтакте]"
                                         "(https://vk.com/{0}?w=wall-{1}_{2}) для его корректного и "
                                         "полного отображения."
                        posts['response']['groups'][0]['screen_name'], posts['response']['groups'][0]['id'], 
                        posts['response']['items'][num]['id']
                        
                        img1 = 'https://i.imgur.com/CjXjcnU.png'
                        img2 = 'https://i.imgur.com/CjXjcnU.png'
                        medias = [types.InputMediaPhoto(img1), types.InputMediaPhoto(img2)]
                        bot.send_media_group(message.from_user.id, medias)
                        """

                        try:
                            # noinspection PyStatementEffect
                            posts[pnum]['attachments']
                            photos = []
                            videos = []
                            for anum in range(len(posts[pnum]['attachments'])):
                                if posts[pnum]['attachments'][anum]['type'] == "photo":
                                    sorted_sizes = sorted(posts[pnum]['attachments'][anum]['photo']['sizes'],
                                                          key=itemgetter('width'))
                                    photos.extend([types.InputMediaPhoto(sorted_sizes[-1]['url'])])
                                elif posts[pnum]['attachments'][anum]['type'] == "video":
                                    video = requests.post("https://api.vk.com/method/video.get",
                                                          data={
                                                              "videos": str(
                                                                  str(posts[pnum]['attachments'][anum]['video']
                                                                      ['owner_id']) + "_" +
                                                                  str(posts[pnum]['attachments'][anum]['video']['id'])
                                                              ),
                                                              "extended": 1,
                                                              "access_token": vk_token,
                                                              "v": "5.80"
                                                          }).json()['response']
                                    video = video['items'][0]

                                    try:
                                        video_platform = str(video['platform'])
                                    except:
                                        video_platform = "VK"

                                    if video_platform == "YouTube":
                                        video_url = "https://www.youtube.com/watch?v={0}".format(
                                            str(video['player']).split("/embed/", 1)[1].split("?__ref=", 1)[0].strip()
                                        )
                                    else:
                                        video_url = "https://vk.com/video{0}_{1}".format(
                                            str(video['owner_id']), str(video['id'])
                                        )

                                    videos.extend([{"url": video_url, "platform": str(video_platform),
                                                    "title": str(video['title']), "duration": str(video['duration'])}])
                                time.sleep(1.25)
                        except Exception as e:
                            photos = None
                            videos = None
                            logging.error("Exception has been occurred while trying to execute the method.",
                                          exc_info=True)

                        # SELECT id FROM TAG_TABLE WHERE 'aaaaaaaa' LIKE '%' || tag_name || '%';
                        markup = types.InlineKeyboardMarkup()
                        markup.row(
                            types.InlineKeyboardButton("🕒 {0}".format(
                                str(datetime.datetime.fromtimestamp(int(posts[pnum]['date'])).strftime("%H:%M"))),
                                callback_data="channel_counters_time|{0}_{1}_{2}".format(
                                                           str(communities[num]['id']), str(posts[pnum]['owner_id']),
                                                           str(posts[pnum]['id']))))
                        markup.row(
                            types.InlineKeyboardButton("💖 {0}".format(
                                str(posts[pnum]['likes']['count'])),
                                callback_data="channel_counters_likes|{0}_{1}_{2}".format(
                                                           str(communities[num]['id']), str(posts[pnum]['owner_id']),
                                                           str(posts[pnum]['id']))),
                            types.InlineKeyboardButton("💬 {0}".format(
                                str(posts[pnum]['comments']['count'])),
                                callback_data="channel_counters_comments|{0}_{1}_{2}".format(
                                                           str(communities[num]['id']), str(posts[pnum]['owner_id']),
                                                           str(posts[pnum]['id']))),
                            types.InlineKeyboardButton("🔁 {0}".format(
                                str(posts[pnum]['reposts']['count'])),
                                callback_data="channel_counters_reposts|{0}_{1}_{2}".format(
                                                           str(communities[num]['id']), str(posts[pnum]['owner_id']),
                                                           str(posts[pnum]['id']))),
                            types.InlineKeyboardButton("👁️ {0}".format(
                                str(posts[pnum]['views']['count'])),
                                callback_data="channel_counters_views|{0}_{1}_{2}".format(
                                                           str(communities[num]['id']), str(posts[pnum]['owner_id']),
                                                           str(posts[pnum]['id'])))
                        )
                        markup.row(
                            types.InlineKeyboardButton("Обновить показатели",
                                                       callback_data="channel_counters_refresh|{0}_{1}_{2}".format(
                                                           str(communities[num]['id']), str(posts[pnum]['owner_id']),
                                                           str(posts[pnum]['id'])))
                        )
                        loop.run_until_complete(Redis.execute("SET", "channel_counters|{0}_{1}_{2}".format(
                            str(communities[num]['id']), str(posts[pnum]['owner_id']), str(posts[pnum]['id'])
                        ), "{0}_{1}_{2}_{3}_{4}".format(
                            str(posts[pnum]['date']),
                            str(posts[pnum]['likes']['count']), str(posts[pnum]['comments']['count']),
                            str(posts[pnum]['reposts']['count']), str(posts[pnum]['views']['count'])
                        )))
                        loop.run_until_complete(Redis.execute("EXPIRE", "channel_counters|{0}_{1}_{2}".format(
                            str(communities[num]['id']), str(posts[pnum]['owner_id']), str(posts[pnum]['id'])
                        ), "1"))

                        formatted_text = "[Оригинальная публикация во ВКонтакте.](https://vk.com/{0}?w=wall-{1}_{2})" \
                                         "\n\n{3}" \
                                         .format(
                                             posts_original['groups'][0]['screen_name'],
                                             posts_original['groups'][0]['id'],
                                             posts[pnum]['id'],
                                             channel.fix_markdown(posts[pnum]['text']))
                        formatted_message = bot.send_message(communities[num]['id'], formatted_text,
                                                             disable_web_page_preview=True, reply_markup=markup,
                                                             parse_mode="Markdown")
                        if photos:
                            bot.send_media_group(communities[num]['id'], photos,
                                                 reply_to_message_id=formatted_message.message_id)
                        time.sleep(1.25)
                time.sleep(900)
            except Exception as e:
                logging.error("Exception has been occurred while trying to execute the method.", exc_info=True)
                return e


if __name__ == "__main__":
    try:
        asyncio.get_event_loop().run_until_complete(PSQL.connection())
        asyncio.get_event_loop().run_until_complete(Redis.connection())

        logging.debug("Bot Settings: " + str(bot.get_me()))

        # noinspection PyTypeChecker
        cPolling = threading.Thread(target=channel.Polling)
        cPolling.setDaemon(True)
        cPolling.start()

        # noinspection PyArgumentList
        bPolling = threading.Thread(target=bot.polling, kwargs={'none_stop': True})
        bPolling.setDaemon(True)
        bPolling.start()

        try:
            while True:
                time.sleep(0.1)
        except:
            pass
    except Exception as e:
        logging.critical("Exception has been occurred while trying to run the application.", exc_info=True)

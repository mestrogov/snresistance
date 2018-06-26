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
import ast


# noinspection PyPep8Naming
class db:
    @staticmethod
    async def connection():
        try:
            postgresql_connection = await asyncpg.connect(host=config.databaseHost,
                                                          database=config.databaseName,
                                                          user=config.databaseUsername,
                                                          port=config.databasePort)

            print('The connection to PostgreSQL can be established successfully.')

            await postgresql_connection.close()
        except Exception as e:
            print("An unexpected error was occurred while calling the method:\n" +
                  str(type(e).__name__) + ': ' + str(e) + ".")

    @classmethod
    async def execute(cls, *args):
        print(*args)
        try:
            postgresql_connection = await asyncpg.connect(host=config.databaseHost,
                                                          database=config.databaseName,
                                                          user=config.databaseUsername,
                                                          port=config.databasePort)

            await postgresql_connection.execute(*args)
            await postgresql_connection.close()
        except Exception as e:
            print("An unexpected error was occurred while calling the method:\n" +
                  str(type(e).__name__) + ': ' + str(e) + ".")

    @classmethod
    async def fetch(cls, *args):
        try:
            postgresql_connection = await asyncpg.connect(host=config.databaseHost,
                                                          database=config.databaseName,
                                                          user=config.databaseUsername,
                                                          port=config.databasePort)

            result = await postgresql_connection.fetch(*args)
            await postgresql_connection.close()

            # The result can be parsed by using: result[0]['COLUMN']
            return result[0]
        except Exception as e:
            print("An unexpected error was occurred while calling the method:\n" +
                  str(type(e).__name__) + ': ' + str(e) + ".")


asyncio.get_event_loop().run_until_complete(db.connection())


bot = telebot.TeleBot(config.botToken)
print(bot.get_me())

botVKSentErrorMessage = None
sentPosts = []

aloop = asyncio.new_event_loop()
asyncio.set_event_loop(aloop)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    try:
        print(call)

        if call.message:
            if call.data == "exit_to_start_menu":
                bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
                start_menu(message=call)
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
                print("OK")
            bot.answer_callback_query(callback_query_id=call.id, show_alert=False)
    except Exception as e:
        try:
            bot.send_message(call.from_user.id,
                             "❗  *Извините, что-то пошло не так, но в скором времени все исправится. "
                             "Попробуйте выполнить то же самое действие через некоторое время (10-15 минут).*",
                             parse_mode="Markdown")
        except:
            pass

        print("An unexpected error was occurred while calling the method:\n" +
              str(type(e).__name__) + ': ' + str(e) + ".")


@bot.message_handler(commands=['start'])
def start_handler(message):
    try:
        print(message)

        if "ru" not in message.from_user.language_code:
            bot.send_message(message.from_user.id,
                             "❗  *Unfortunately, the bot doesn't speak your language. So if you are "
                             "not able to understand the text that is written below, use an online translator "
                             "such as Google Translate.*",
                             parse_mode="Markdown")

        bot.send_message(message.from_user.id, config.startMessage, parse_mode="Markdown")
        start_menu(message)

        _aloop = asyncio.new_event_loop()
        asyncio.set_event_loop(_aloop)

        _aloop.run_until_complete(db.execute(
            'INSERT INTO users("id") VALUES($1) RETURNING "id", "is_paid", "vk_token", "communities";',
            message.from_user.id
        ))
    except Exception as e:
        try:
            bot.send_message(message.from_user.id,
                             "❗  *Извините, что-то пошло не так, но в скором времени все исправится. "
                             "Попробуйте выполнить то же самое действие через некоторое время (10-15 минут).*",
                             parse_mode="Markdown")
        except:
            pass

        print("An unexpected error was occurred while calling the method:\n" +
              str(type(e).__name__) + ': ' + str(e) + ".")


def start_menu(message):
    try:
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
                             "❗  *Извините, что-то пошло не так, но в скором времени все исправится. "
                             "Попробуйте выполнить то же самое действие через некоторое время (10-15 минут).*",
                             parse_mode="Markdown")
        except:
            pass

        print("An unexpected error was occurred while calling the method:\n" +
              str(type(e).__name__) + ': ' + str(e) + ".")


@bot.message_handler(commands=['debug'])
def command_debug(message):
    try:
        _aloop = asyncio.new_event_loop()
        asyncio.set_event_loop(_aloop)

        is_paid = _aloop.run_until_complete(db.fetch(
            'SELECT is_paid FROM users WHERE id = $1;',
            message.from_user.id
        ))['is_paid']
        communities = _aloop.run_until_complete(db.fetch(
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
                             "❗  *Извините, что-то пошло не так, но в скором времени все будет исправлено. "
                             "Попробуйте выполнить то же самое действие через некоторое время (10-15 минут).*",
                             parse_mode="Markdown")
        except:
            pass

        print("An unexpected error was occurred while calling the method:\n" +
              str(type(e).__name__) + ': ' + str(e) + ".")


@bot.message_handler(commands=['add', 'subscribe', 'sub'])
def command_add(message):
    try:
        _aloop = asyncio.new_event_loop()
        asyncio.set_event_loop(_aloop)

        communities = []
        communities_old = _aloop.run_until_complete(db.fetch(
            'SELECT communities FROM users WHERE id = $1;',
            message.from_user.id
        ))['communities']
        print(communities_old)
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
                _aloop.run_until_complete(db.execute(
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
                             "❗  *Извините, что-то пошло не так, но в скором времени все будет исправлено. "
                             "Попробуйте выполнить то же самое действие через некоторое время (10-15 минут).*",
                             parse_mode="Markdown")
        except:
            pass

        print("An unexpected error was occurred while calling the method:\n" +
              str(type(e).__name__) + ': ' + str(e) + ".")


@bot.message_handler(commands=['remove', 'unsubscribe', 'unsub'])
def command_remove(message):
    try:
        _aloop = asyncio.new_event_loop()
        asyncio.set_event_loop(_aloop)

        communities = []
        communities_db = _aloop.run_until_complete(db.fetch(
            'SELECT communities FROM users WHERE id = $1;',
            message.from_user.id
        ))['communities']
        print(communities_db)
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
                _aloop.run_until_complete(db.execute(
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
                             "❗  *Извините, что-то пошло не так, но в скором времени все будет исправлено. "
                             "Попробуйте выполнить то же самое действие через некоторое время (10-15 минут).*",
                             parse_mode="Markdown")
        except:
            pass

        print("An unexpected error was occurred while calling the method:\n" +
              str(type(e).__name__) + ': ' + str(e) + ".")


@bot.message_handler(commands=['addchannel'])
def command_addchannel(message):
    try:
        bot.send_message(message.from_user.id,
                         "Вы решили создать канал, добавьте меня в него и напишите команду: "
                         "`/initchannel@SNResistance {0}_id`",
                         parse_mode="Markdown")
    except Exception as e:
        try:
            bot.send_message(message.from_user.id,
                             "❗  *Извините, что-то пошло не так, но в скором времени все будет исправлено. "
                             "Попробуйте выполнить то же самое действие через некоторое время (10-15 минут).*",
                             parse_mode="Markdown")
        except:
            pass

        print("An unexpected error was occurred while calling the method:\n" +
              str(type(e).__name__) + ': ' + str(e) + ".")


@bot.channel_post_handler()
def initchannel(message):
    try:
        print("----------")
        print("Channel Name: " + str(message.chat.title))
        print("Channel ID: " + str(message.chat.id))

        _aloop = asyncio.new_event_loop()
        asyncio.set_event_loop(_aloop)

        if "!initchannel" in message.text:
            command = message.text.replace("!initchannel", "").strip().split("|")

            user_id = int(command[0])
            print(user_id)
            user_vktoken = _aloop.run_until_complete(db.fetch(
                'SELECT vk_token FROM users WHERE id = $1;',
                int(user_id)
            ))['vk_token']
            print(user_vktoken)

            community = requests.post("https://api.vk.com/method/groups.getById",
                                      data={
                                          "group_id": str(command[1]),
                                          "fields": "description",
                                          "access_token": str(user_vktoken),
                                          "v": "5.78"
                                      }).json()['response'][0]
            print(community)

            channel_id = message.chat.id
            init_date = calendar.timegm(datetime.datetime.utcnow().utctimetuple())

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
                pinned_post = config.channelDescription + "\n\n\n\n" + str(community['description'])
                pin_id = bot.send_message(channel_id, pinned_post)
                bot.pin_chat_message(channel_id, pin_id.json['message_id'])
            except:
                bot.send_message(user_id,
                                 "Не удалось отправить сообщение и закрепить его в канале.")
                return

            try:
                bot.set_chat_description(channel_id, config.channelDescription)
            except:
                bot.send_message(user_id,
                                 "Не удалось изменить описание канала (или оно не было изменено).")

            aloop.run_until_complete(db.execute(
                'INSERT INTO channels("id", "owner_id", "community_id", "initiation_date") '
                'VALUES($1, $2, $3, $4) RETURNING "id", "owner_id", "community_id", "initiation_date";',
                int(channel_id), int(user_id), int(community['id']), int(init_date)
             ))

            bot.send_message(int(user_id),
                             "Ваш канал успешно настроен и готов для получения новых постов.")
    except Exception as e:
        try:
            bot.send_message(message.from_user.id,
                             "❗  *Извините, что-то пошло не так, но в скором времени все будет исправлено. "
                             "Попробуйте выполнить то же самое действие через некоторое время (10-15 минут).*",
                             parse_mode="Markdown")
        except:
            pass

        print("An unexpected error was occurred while calling the method:\n" +
              str(type(e).__name__) + ': ' + str(e) + ".")


"""
def post_polling():
    global bot
    global botVKSentErrorMessage
    global sentPosts
    while True:
        try:
            print("sentPosts:" + str(sentPosts))
            for groupID in config.vkGroupsIDs:
                try:
                    print(len(config.vkAccessTokens))

                    posts_count = 10
                    for pnum in range(len(config.vkAccessTokens)):
                        posts = requests.post("https://api.vk.com/method/wall.get",
                                              data={
                                                  "owner_id": str("-" + str(groupID)),
                                                  "offset": 1,
                                                  "count": posts_count,
                                                  "filter": "all",
                                                  "extended": 1,
                                                  "access_token": config.vkAccessTokens[pnum],
                                                  "v": "5.78"
                                              })

                        try:
                            posts.json()['error']
                        except:
                            print("wall.get, using specified access_token: " + str(config.vkAccessTokens[pnum]))
                            break

                    # print(posts.text)
                    # noinspection PyUnboundLocalVariable
                    posts = posts.json()

                    # noinspection PyStatementEffect
                    posts['response']

                    if botVKSentErrorMessage:
                        botVKSentErrorMessage = False
                except Exception as e:
                    if botVKSentErrorMessage:
                        pass
                    else:
                        bot.send_message(config.botChannelID, "❗*Что-то пошло не так при получении публикаций "
                                                              "с помощью VK API. Следующий запрос к VK API для "
                                                              "получения последних постов из сообществ будет "
                                                              "произведен через 15 минут. В случае решения данной "
                                                              "проблемы, сообщение просто будет удалено.*",
                                         parse_mode="Markdown", disable_notification=True)
                        botVKSentErrorMessage = True

                    print("VK Exception Handling: An error has occurred: " + str(e) + ". Next request to VK API in "
                                                                                      "15 minutes.")
                    time.sleep(900)

                # noinspection PyUnboundLocalVariable
                for num in range(posts_count):
                    # noinspection PyBroadException
                    try:
                        # noinspection PyStatementEffect
                        posts['response']['items'][num]['attachments'][0]
                        attachments = True
                    except:
                        attachments = False

                    # print(int(int(time.time()) - posts['response']['items'][num]['date']))
                    if int(int(time.time()) - posts['response']['items'][num]['date']) <= 2700:
                        if "{0}_{1}".format(
                            posts['response']['groups'][0]['id'],
                            posts['response']['items'][num]['id']
                        ) in sentPosts:
                            pass
                        else:
                            print("group: " + str(posts['response']['groups'][0]['id']))
                            print("posts: " + str(posts['response']['items'][num]['id']))
                            sentPosts.append("{0}_{1}".format(
                                posts['response']['groups'][0]['id'],
                                posts['response']['items'][num]['id']
                            ))
                            print("sentPosts.append: " + str(sentPosts))

                            post_text = posts['response']['items'][num]['text']
                            try:
                                post_text_part = post_text.partition('[')[-1].rpartition(']')[0]
                                post_text_splitted = post_text_part.split("|")
                                post_text_md = "[" + str(post_text_splitted[1]) + "]" + \
                                               "(https://vk.com/" + str(post_text_splitted[0]) + ")"
                                post_text = post_text.replace("[" + post_text_part + "]", post_text_md)
                            except:
                                pass

                            try:
                                post_text_stripping = post_text
                                text = {tag.strip("#") for tag in post_text_stripping.split() if tag.startswith("#")}
                                text = list(text)
                                for it in text:
                                    _t = "#" + it
                                    post_text = post_text.replace(_t, "")
                            except:
                                pass

                            if attachments:
                                bot.send_message(config.botChannelID,
                                                 "[Новая публикация в сообществе " + posts['response']['groups'][0]
                                                 ['name'] + " во ВКонтакте.](https://vk.com/{0}?w=wall-{1}_{2})"
                                                 "\n\n\n{3}"
                                                 "\n\n\n❗️К данной публикации что-то прикреплено, "
                                                 "[перейдите на этот пост во ВКонтакте]"
                                                 "(https://vk.com/{0}?w=wall-{1}_{2}) для его корректного и "
                                                 "полного отображения."
                                                 "\n\n🕒 _Время публикации: {4}_"
                                                 "\n👁 _Просмотров: {5}_"
                                                 "\n👍 _Лайков: {6}_"
                                                 "\n📎 _Комментариев: {7}_"
                                                 .format(posts['response']['groups'][0]['screen_name'],
                                                         posts['response']['groups'][0]['id'],
                                                         posts['response']['items'][num]['id'],
                                                         post_text,
                                                         datetime.datetime.fromtimestamp(
                                                             int(posts['response']['items'][num]['date'])
                                                         ).strftime("%H:%M"),
                                                         posts['response']['items'][num]['views']['count'],
                                                         posts['response']['items'][num]['likes']['count'],
                                                         posts['response']['items'][num]['comments']['count']
                                                         ),
                                                 parse_mode="Markdown")
                            else:
                                bot.send_message(config.botChannelID,
                                                 "[Новая публикация в сообществе " + posts['response']['groups'][0]
                                                 ['name'] + " во ВКонтакте.](https://vk.com/{0}?w=wall-{1}_{2})"
                                                 "\n\n\n{3}"
                                                 "\n\n🕒 _Время публикации: {4}_"
                                                 "\n👁 _Просмотров: {5}_"
                                                 "\n👍 _Лайков: {6}_"
                                                 "\n📎 _Комментариев: {7}_"
                                                 .format(posts['response']['groups'][0]['screen_name'],
                                                         posts['response']['groups'][0]['id'],
                                                         posts['response']['items'][num]['id'],
                                                         post_text,
                                                         datetime.datetime.fromtimestamp(
                                                             int(posts['response']['items'][num]['date'])
                                                         ).strftime("%H:%M"),
                                                         posts['response']['items'][num]['views']['count'],
                                                         posts['response']['items'][num]['likes']['count'],
                                                         posts['response']['items'][num]['comments']['count']
                                                         ),
                                                 parse_mode="Markdown")
                time.sleep(1.25)
            time.sleep(600)
        except Exception as e:
            print("Bot Exception Handling: An error has occurred: " + str(e) + ".")
"""

try:
    bot.polling(none_stop=True)
except Exception as e:
    print("An unexpected error was occurred while calling the method:\n" +
          str(type(e).__name__) + ': ' + str(e) + ".")

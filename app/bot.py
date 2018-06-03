# -*- coding: utf-8 -*-

import requests
# noinspection PyPackageRequirements
import telebot
from telebot import types
# noinspection PyPackageRequirements,PyUnresolvedReferences
import config as config
import time
import datetime
import threading

bot = telebot.TeleBot(config.botToken)
botVKSentErrorMessage = None
sentPosts = []


@bot.channel_post_handler()
def handler(message):
    print("----------")
    print("Channel Name: " + str(message.chat.title))
    print("Channel ID: " + str(message.chat.id))


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


if __name__ == "__main__":
    post_polling = threading.Thread(target=post_polling())
    bot_polling = threading.Thread(target=bot.polling(none_stop=True))

    post_polling.daemon = True
    bot_polling.daemon = True

    post_polling.start()
    bot_polling.start()

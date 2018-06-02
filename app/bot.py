# -*- coding: utf-8 -*-

import requests
# noinspection PyPackageRequirements
import telebot
# noinspection PyPackageRequirements,PyUnresolvedReferences
import config as config
import time
import datetime

bot = telebot.TeleBot(config.botToken)
sentPosts = []


"""
@bot.channel_post_handler()
def handler(message):
    print(message)
"""

try:
    while True:
        try:
            print("sentPosts:" + str(sentPosts))
            for groupID in config.vkGroupsIDs:
                try:
                    group = requests.post("https://api.vk.com/method/groups.getById",
                                          data={
                                              "group_ids": groupID,
                                              "access_token": config.vkAccessToken,
                                              "v": "5.78"
                                          })
                    print(group.text)
                    group = group.json()

                    posts_count = 10
                    posts = requests.post("https://api.vk.com/method/wall.get",
                                          data={
                                              "owner_id": str("-" + str(groupID)),
                                              "offset": 1,
                                              "count": posts_count,
                                              "filter": "all",
                                              "extended": 1,
                                              "access_token": config.vkAccessToken,
                                              "v": "5.78"
                                          })
                    print(posts.text)
                    posts = posts.json()
                    # print(posts)
                    # print(str(int(time.time())))

                    # noinspection PyStatementEffect
                    group['response']
                    # noinspection PyStatementEffect
                    posts['response']
                except Exception as e:
                    num = 0
                    posts_count = 0
                    posts = None
                    group = None

                    bot.send_message(config.botChannelID, "❗*Что-то пошло не так при получении публикаций с помощью "
                                                          "VK API. Следующий запрос к VK API для получения последних "
                                                          "постов из сообществ будет произведен через 15 минут. "
                                                          "В случае повторной неудачи будет опубликовано такое же "
                                                          "сообщение.*",
                                     parse_mode="Markdown")
                    print("VK Exception Handling: An error has occurred: " + str(e) + ". Next request to VK API in "
                                                                                      "15 minutes.")
                    time.sleep(900)

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
                            group['response'][0]['id'],
                            posts['response']['items'][num]['id']
                        ) in sentPosts:
                            pass
                        else:
                            print("group: " + str(group['response'][0]['id']))
                            print("posts: " + str(posts['response']['items'][num]['id']))
                            sentPosts.append("{0}_{1}".format(
                                group['response'][0]['id'],
                                posts['response']['items'][num]['id']
                            ))
                            print("sentPosts.append: " + str(sentPosts))
                            if attachments:
                                bot.send_message(config.botChannelID,
                                                 "[Новая публикация в сообществе " + group['response'][0]['name'] +
                                                 " во ВКонтакте.](https://vk.com/{0}?w=wall-{1}_{2})"
                                                 "\n\n\n\\{3}\\"
                                                 "\n\n\n❗️К данной публикации что-то прикреплено, "
                                                 "[перейдите на этот пост во ВКонтакте]"
                                                 "(https://vk.com/{0}?w=wall-{1}_{2}) для его корректного и "
                                                 "полного отображения."
                                                 "\n\n🕒 _Время публикации: {4}_"
                                                 "\n👁 _Просмотров: {5}_"
                                                 "\n👍🏻 _Лайков: {6}_"
                                                 "\n📎 _Комментариев: {7}_"
                                                 .format(group['response'][0]['screen_name'],
                                                         group['response'][0]['id'],
                                                         posts['response']['items'][num]['id'],
                                                         posts['response']['items'][num]['text'],
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
                                                 "[Новая публикация в сообществе " + group['response'][0]['name'] +
                                                 " во ВКонтакте.](https://vk.com/{0}?w=wall-{1}_{2})"
                                                 "\n\n\n\\{3}\\"
                                                 "\n\n🕒 _Время публикации: {4}_"
                                                 "\n👁 _Просмотров: {5}_"
                                                 "\n👍🏻 _Лайков: {6}_"
                                                 "\n📎 _Комментариев: {7}_"
                                                 .format(group['response'][0]['screen_name'],
                                                         group['response'][0]['id'],
                                                         posts['response']['items'][num]['id'],
                                                         posts['response']['items'][num]['text'],
                                                         datetime.datetime.fromtimestamp(
                                                             int(posts['response']['items'][num]['date'])
                                                         ).strftime("%H:%M"),
                                                         posts['response']['items'][num]['views']['count'],
                                                         posts['response']['items'][num]['likes']['count'],
                                                         posts['response']['items'][num]['comments']['count']
                                                         ),
                                                 parse_mode="Markdown")
                time.sleep(1.5)
            time.sleep(45)
        except Exception as e:
            print("Bot Exception Handling: An error has occurred: " + str(e) + ".")
except Exception as e:
    print("While True Exception Handling: An error has occurred: " + str(e) + ".")


bot.polling(1)

# -*- coding: utf-8 -*-

import requests
# noinspection PyPackageRequirements
import telebot
# noinspection PyPackageRequirements,PyUnresolvedReferences
import config as config
import time

bot = telebot.TeleBot(config.botToken)


"""
@bot.channel_post_handler()
def handler(message):
    print(message)
"""

try:
    while True:
        for groupID in config.vkGroupsIDs:
            group = requests.post("https://api.vk.com/method/groups.getById",
                                  data={
                                      "group_ids": groupID,
                                      "access_token": config.vkAccessToken,
                                      "v": "5.78"
                                  })
            group = group.json()

            posts_count = 25
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
            posts = posts.json()
            # print(posts)
            # print(str(int(time.time())))

            for num in range(posts_count):
                try:
                    # noinspection PyStatementEffect
                    posts['response']['items'][num]['attachments'][0]
                    attachments = True
                except:
                    attachments = False

                print(int(int(time.time()) - posts['response']['items'][num]['date']))
                if int(int(time.time()) - posts['response']['items'][num]['date']) <= 220:
                    if attachments:
                        bot.send_message(config.botChannelID,
                                         "[Новая публикация в паблике " + group['response'][0]['name'] +
                                         ".](https://vk.com/{0}?w=wall-{1}_{2})"
                                         "\n\n\n*{3}*"
                                         "\n\n\n❗️К данной публикации что-то прикреплено, [перейдите на этот пост во "
                                         "ВКонтакте](https://vk.com/{0}?w=wall-{1}_{2}) для его "
                                         "корректного и полного отображения."
                                         "\n\n👁 _Просмотров: {4}_"
                                         "\n👍🏻 _Лайков: {5}_"
                                         "\n📎 _Комментариев: {6}_"
                                         .format(group['response'][0]['screen_name'],
                                                 group['response'][0]['id'],
                                                 posts['response']['items'][num]['id'],
                                                 posts['response']['items'][num]['text'],
                                                 posts['response']['items'][num]['views']['count'],
                                                 posts['response']['items'][num]['likes']['count'],
                                                 posts['response']['items'][num]['comments']['count']
                                                 ),
                                         parse_mode="Markdown")
                    else:
                        bot.send_message(config.botChannelID,
                                         "[Новая публикация в паблике " + group['response'][0]['name'] +
                                         ".](https://vk.com/{0}?w=wall-{1}_{2})"
                                         "\n\n\n*{3}*"
                                         "\n\n\n👁 _Просмотров: {4}_"
                                         "\n👍🏻 _Лайков: {5}_"
                                         "\n📎 _Комментариев: {6}_"
                                         .format(group['response'][0]['screen_name'],
                                                 group['response'][0]['id'],
                                                 posts['response']['items'][num]['id'],
                                                 posts['response']['items'][num]['text'],
                                                 posts['response']['items'][num]['views']['count'],
                                                 posts['response']['items'][num]['likes']['count'],
                                                 posts['response']['items'][num]['comments']['count']
                                                 ),
                                         parse_mode="Markdown")
            time.sleep(0.05)
        time.sleep(120)
except Exception as e:
    print("An error has occurred: " + str(e) + ".")


bot.polling(1)

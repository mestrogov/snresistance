# -*- coding: utf-8 -*-

from app import logging
from app import config as config
from app.utils.markup_fixes import markup_multipurpose_fixes as markup_fixes
from app.utils.markup_fixes import escape_markdown_links as escape_md_links
from app.utils.list_splitting import split_list as split_list
from app.remote.postgresql import Psql as psql
from app.utils.post_statistics import statistics as postStatistics
from telegram import InputMediaPhoto
from operator import itemgetter
import logging
import asyncio
import requests
import time


def polling(bot, job):
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        communities = loop.run_until_complete(psql.fetch(
            'SELECT id, owner_id, community_id FROM channels;',
        ))

        for num in range(len(communities)):
            if config.developerMode:
                loop.run_until_complete(psql.execute(
                    'DELETE FROM posts WHERE chat_id = $1;',
                    int(communities[num]['id'])
                ))
                logging.debug("Developer Mode enabled, all posts are deleted in the every communities loop.")
            access_token = loop.run_until_complete(psql.fetchrow(
                'SELECT access_token FROM users WHERE id = $1;',
                communities[num]['owner_id']
            ))['access_token']

            posts = requests.post("https://api.vk.com/method/wall.get",
                                  data={
                                      "owner_id": str("-" + str(communities[num]['community_id'])),
                                      "count": 10,
                                      "filter": "all",
                                      "extended": 1,
                                      "access_token": access_token,
                                      "v": "5.80"
                                  }).json()

            posts_original = posts['response']
            posts_items = posts['response']['items']

            for pnum in range(len(posts_items)):
                time.sleep(1)
                posts = posts_items[pnum]
                is_posted = loop.run_until_complete(psql.fetchrow(
                    'SELECT post_id FROM posts WHERE chat_id = $1 AND community_id = $2 AND post_id = $3;',
                    int(communities[num]['id']), int(posts['owner_id']), int(posts['id'])
                ))

                try:
                    if is_posted:
                        continue
                except:
                    pass

                try:
                    if str(posts["marked_as_ads"]) == "1":
                        continue
                except:
                    pass

                attachments = None
                is_repost = None
                video_preview = None
                posts['text_reposted'] = None
                photos = None
                videos = None
                audios = None
                links = None
                other = None

                try:
                    posts['copy_history']
                    is_repost = True

                    try:
                        posts['copy_history'][0]['attachments']
                    except KeyError:
                        pass

                    try:
                        posts['attachments']
                    except KeyError:
                        posts['attachments'] = []

                    try:
                        posts_original['profiles']
                    except KeyError:
                        posts_original['profiles'] = []

                    posts['attachments'].extend(posts['copy_history'][0]['attachments'])
                    posts['text_reposted'] = posts['copy_history'][0]['text']
                except KeyError:
                    logging.debug("KeyError Exception has been occurred, most likely the post isn't a repost.",
                                  exc_info=True)

                try:
                    try:
                        posts['attachments']

                        attachments = True
                        photos = []
                        videos = []
                        audios = []
                        links = []
                        other = []

                        for anum in range(len(posts['attachments'])):
                            if posts['attachments'][anum]['type'] == "photo":
                                sorted_sizes = sorted(posts['attachments'][anum]['photo']['sizes'],
                                                      key=itemgetter('width'))
                                photos.extend([InputMediaPhoto(sorted_sizes[-1]['url'])])
                            elif posts['attachments'][anum]['type'] == "video" or \
                                    ("youtube.com/watch?v=" in posts['attachments'][anum]['link']['url'] if
                                        posts['attachments'][anum]['type'] == "link" else None):
                                if posts['attachments'][anum]['type'] == "video":
                                    time.sleep(1)
                                    video = requests.post("https://api.vk.com/method/video.get",
                                                          data={
                                                              "videos": str(
                                                                  str(posts['attachments'][anum]['video']
                                                                      ['owner_id']) + "_" +
                                                                  str(posts['attachments'][anum]['video']['id'])
                                                              ),
                                                              "extended": 1,
                                                              "access_token": access_token,
                                                              "v": "5.80"
                                                          }).json()['response']
                                    try:
                                        video = video['items'][0]
                                    except (KeyError, IndexError):
                                        continue
                                    try:
                                        video_platform = str(video['platform'])
                                    except:
                                        video_platform = "VK"

                                    if video_platform == "YouTube":
                                        video_url = "https://www.youtube.com/watch?v={0}".format(
                                            str(video['player']).split("/embed/", 1)[1].split("?__ref=", 1)[0].
                                            strip())
                                        video_url = video_url.replace("&feature=share", "", 1).strip()
                                    else:
                                        video_url = str(video['player']).split("&__ref=", 1)[0].strip()

                                    videos.extend([{"url": video_url, "platform": str(video_platform),
                                                    "title": str(video['title'])}])
                                if posts['attachments'][anum]['type'] == "link" and \
                                        "youtube.com/watch?v=" in posts['attachments'][anum]['link']['url']:
                                    video_platform = "YouTube"
                                    video_url = posts['attachments'][anum]['link']['url'].\
                                        replace("&feature=share", "", 1).strip()

                                    videos.extend([{"url": video_url, "platform": str(video_platform),
                                                    "title": str(posts['attachments'][anum]['link']['title'])}])
                            elif posts['attachments'][anum]['type'] == "audio":
                                audios.extend([{"artist": str(posts['attachments'][anum]['audio']['artist']),
                                                "title": str(posts['attachments'][anum]['audio']['title'])}])
                            elif posts['attachments'][anum]['type'] == "link":
                                links.extend([{"title": str(posts['attachments'][anum]['link']['title']),
                                               "url": str(posts['attachments'][anum]['link']['url'])}])
                            else:
                                if str(posts['attachments'][anum]['type']) != "poll":
                                    other.extend([{"type": str(posts['attachments'][anum]['type'])}])
                    except KeyError:
                        logging.debug("KeyError Exception has been occurred, most likely the post doesn't have "
                                      "any attachments.", exc_info=True)
                except Exception as e:
                    logging.error("Exception has been occurred while trying to execute attachments check.",
                                  exc_info=True)

                post_profile = None
                repost_profile = None
                posts_original['profiles'].extend(posts_original['groups'])

                for i in range(len(posts_original['profiles'])):
                    if str(posts_original['profiles'][i]['id']) == str(posts['owner_id']).replace("-", "", 1):
                        post_profile = posts_original['profiles'][i]
                    if is_repost:
                        if str(posts_original['profiles'][i]['id']) == str(posts['copy_history'][0]['owner_id']).\
                                replace("-", "", 1):
                            repost_profile = posts_original['profiles'][i]
                try:
                    if is_repost:
                        repost_profile['name']
                except KeyError:
                    repost_profile['name'] = str(repost_profile['first_name']) + " " + str(repost_profile['last_name'])

                if posts['text']:
                    post_text = "\n\n" + str(markup_fixes(posts['text']))
                else:
                    post_text = ""
                if is_repost:
                    post_text = str(post_text) + "\n\n🔁 Репост со страницы {0}.\n".\
                        format(
                            str(escape_md_links(repost_profile['name']))) + \
                        str(markup_fixes(posts['text_reposted']))

                formatted_text = "[Оригинальная публикация.](https://vk.com/wall-{0}_{1})" \
                                 "{2}".format(
                                     str(post_profile['id']),
                                     str(posts['id']),
                                     str(post_text))
                if attachments:
                    if videos or audios or links or other:
                        formatted_text = formatted_text + str("\n\n*Прикрепленные вложения к публикации:*")
                    aint = 1
                    if videos:
                        for vint in range(len(videos)):
                            formatted_text = formatted_text + "\n{0}. Видеозапись — [{1}]({2}) — {3}".format(
                                str(int(aint)), str(escape_md_links(videos[vint]['title'])), str(videos[vint]['url']),
                                str(videos[vint]['platform'])
                            )
                            if videos[vint]['platform'] == "YouTube" and not video_preview:
                                formatted_text = formatted_text.replace("[О", "[О]({0})[".format(
                                    videos[vint]['url']
                                ), 1)
                                video_preview = True
                            aint += 1
                    if audios:
                        for auint in range(len(audios)):
                            formatted_text = formatted_text + \
                                             "\n{0}. Аудиозапись — {1} — {2}".format(
                                                 str(int(aint)), str(escape_md_links(audios[auint]['artist'])),
                                                 str(escape_md_links(audios[auint]['title'])).replace("(", "").
                                                 replace(")", ""))
                            aint += 1
                    if links:
                        for lint in range(len(links)):
                            formatted_text = formatted_text + \
                                             "\n{0}. Ссылка на сторонний сайт — [{1}]({2})".format(
                                                 str(int(aint)), str(escape_md_links(links[lint]['title'])),
                                                 str(links[lint]['url']))
                            aint += 1
                        if not video_preview:
                            formatted_text = formatted_text.replace("[О", "[О]({0})[".format(
                                links[0]['url']
                            ), 1)
                    if other:
                        for oint in range(len(other)):
                            formatted_text = formatted_text + \
                                             "\n{0}. К данной публикации прикреплено вложение с типом *{1}*. " \
                                             "Данный тип не может быть отображен внутри Telegram. Для его " \
                                             "просмотра перейдите на данную публикацию во ВКонтакте.".format(
                                                 str(int(aint)), str(other[oint]['type']))
                            aint += 1

                try:
                    if photos:
                        photos = split_list(photos, 10)
                        for lphotos in range(len(photos)):
                            bot.send_media_group(communities[num]['id'], photos[lphotos], timeout=60)

                    markup = postStatistics(bot, posts=posts, chat_id=communities[num]['id'], mtype="initiate")
                    if video_preview or links:
                        message = bot.send_message(communities[num]['id'], formatted_text, reply_markup=markup,
                                                   parse_mode="Markdown", timeout=30)
                    else:
                        message = bot.send_message(communities[num]['id'], formatted_text,
                                                   disable_web_page_preview=True, reply_markup=markup,
                                                   parse_mode="Markdown", timeout=30)
                    try:
                        if str(posts["is_pinned"]) == "1":
                            bot.pin_chat_message(communities[num]['id'], message.message_id)
                    except KeyError:
                        pass

                    loop.run_until_complete(psql.execute(
                        'INSERT INTO posts("chat_id", "message_id", "community_id", "post_id") '
                        'VALUES($1, $2, $3, $4) RETURNING "chat_id", "community_id", "post_id";',
                        int(communities[num]['id']), int(message.message_id), int(posts['owner_id']),
                        int(posts['id'])))
                except Exception as e:
                    logging.error("Exception has been occurred while trying to send message to the channel.",
                                  exc_info=True)
    except Exception as e:
        logging.error("Exception has been occurred while trying to execute the method.", exc_info=True)
        return e

# -*- coding: utf-8 -*-

from app import logging
from app import config as config
from app.utils.markup_fixes import markup_multipurpose_fixes as markup_fixes
from app.remote.postgresql import Psql as psql
from app.utils.post_statistics import statistics as postStatistics
from telegram import InputMediaPhoto
from telegram.ext.dispatcher import run_async
from operator import itemgetter
import logging
import asyncio
import requests
import time


try:
    # noinspection PyUnresolvedReferences
    from app.bot import bot_configuration as botConfiguration
except ImportError:
    logging.debug("bot_configuration is already imported in the other module, skipped.")


@run_async
def polling():
    while True:
        try:
            bot = botConfiguration()
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            communities = loop.run_until_complete(psql.fetch(
                'SELECT id, owner_id, community_id FROM channels;',
            ))

            for num in range(len(communities)):
                time.sleep(0.5)

                vk_token = loop.run_until_complete(psql.fetchrow(
                    'SELECT vk_token FROM users WHERE id = $1;',
                    communities[num]['owner_id']
                ))['vk_token']

                posts = requests.post("https://api.vk.com/method/wall.get",
                                      data={
                                          "owner_id": str("-" + str(communities[num]['community_id'])),
                                          "count": 3,
                                          "filter": "all",
                                          "extended": 1,
                                          "access_token": vk_token,
                                          "v": "5.80"
                                      }).json()

                posts_original = posts['response']
                posts = posts['response']['items']

                for pnum in range(len(posts)):
                    posts = posts[pnum]
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
                    photos = None
                    videos = None
                    audios = None
                    links = None

                    try:
                        try:
                            # noinspection PyStatementEffect
                            posts['attachments']

                            attachments = True
                            photos = []
                            videos = []
                            audios = []
                            links = []

                            for anum in range(len(posts['attachments'])):
                                if posts['attachments'][anum]['type'] == "photo":
                                    sorted_sizes = sorted(posts['attachments'][anum]['photo']['sizes'],
                                                          key=itemgetter('width'))
                                    photos.extend([InputMediaPhoto(sorted_sizes[-1]['url'])])
                                elif posts['attachments'][anum]['type'] == "video":
                                    time.sleep(0.5)
                                    video = requests.post("https://api.vk.com/method/video.get",
                                                          data={
                                                              "videos": str(
                                                                  str(posts['attachments'][anum]['video']
                                                                      ['owner_id']) + "_" +
                                                                  str(posts['attachments'][anum]['video']['id'])
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
                                    time.sleep(1)
                                elif posts['attachments'][anum]['type'] == "audio":
                                    audios.extend([{"artist": str(posts['attachments'][anum]['audio']['artist']),
                                                    "title": str(posts['attachments'][anum]['audio']['title'])}])
                                elif posts['attachments'][anum]['type'] == "link":
                                    links.extend([{"title": str(posts['attachments'][anum]['link']['title']),
                                                   "url": str(posts['attachments'][anum]['link']['url'])}])
                        except KeyError:
                            logging.debug("There is no attachments in this post: " + str(posts['owner_id']) +
                                          "_" + str(posts['id']) + ".")
                    except Exception as e:
                        logging.error("Exception has been occurred while trying to execute attachments check.",
                                      exc_info=True)

                    # SELECT id FROM TAG_TABLE WHERE 'aaaaaaaa' LIKE '%' || tag_name || '%';
                    markup, poll = postStatistics(bot,
                                                  posts=posts, chat_id=communities[num]['id'], mtype="initiate")

                    template_text = "[Оригинальная публикация во ВКонтакте.](https://vk.com/{0}?w=wall-{1}_{2})" \
                                    "\n\n{3}".format(
                                         str(posts_original['groups'][0]['screen_name']),
                                         str(posts_original['groups'][0]['id']),
                                         str(posts['id']),
                                         str(markup_fixes(posts['text']))
                                     )
                    formatted_text = template_text
                    if attachments:
                        formatted_text = formatted_text + str("\n\n*Прикрепленные вложения к публикации:*")
                        aint = 1
                        if photos:
                            formatted_text = formatted_text + str("\n{0}. Все прикрепленные к публикации "
                                                                  "фотографии отправлены в ответе на данное "
                                                                  "сообщение.".format(str(aint)))
                            aint += 1
                        if poll:
                            formatted_text = formatted_text + str("\n{0}. Опрос прикреплен в виде кнопок к этому "
                                                                  "сообщению.".format(str(aint)))
                            aint += 1
                        if videos:
                            for vint in range(len(videos)):
                                formatted_text = formatted_text + "\n{0}. Видеозапись — [{1}]({2}) — {3}".format(
                                    str(int(aint)), str(videos[vint]['title']), str(videos[vint]['url']),
                                    str(videos[vint]['platform'])
                                )
                                aint += 1
                            if not links:
                                formatted_text = formatted_text.replace("[О", "[О]({0})[".format(
                                    videos[0]['url']
                                ), 1)
                        if audios:
                            for auint in range(len(audios)):
                                formatted_text = formatted_text + \
                                                 "\n{0}. Аудиозапись — [{1} — {2}](https://soundcloud.com/" \
                                                 "search?q={1}-{2}) — SoundCloud".format(
                                                     str(int(aint)), str(audios[auint]['artist']),
                                                     str(audios[auint]['title']))
                                aint += 1
                        if links:
                            for lint in range(len(links)):
                                formatted_text = formatted_text + \
                                                 "\n{0}. Ссылка — [{1}]({2})".format(
                                                     str(int(aint)), str(links[lint]['title']),
                                                     str(links[lint]['url']))
                                aint += 1
                            formatted_text = formatted_text.replace("[О", "[О]({0})[".format(
                                links[0]['url']
                            ), 1)

                    try:
                        if videos or links:
                            message = bot.send_message(communities[num]['id'], formatted_text, reply_markup=markup,
                                                       parse_mode="Markdown")
                        else:
                            message = bot.send_message(communities[num]['id'], formatted_text,
                                                       disable_web_page_preview=True, reply_markup=markup,
                                                       parse_mode="Markdown")
                        if photos:
                            bot.send_media_group(communities[num]['id'], photos,
                                                 reply_to_message_id=message.message_id)

                        if not config.developerMode:
                            loop.run_until_complete(psql.execute(
                                'INSERT INTO posts("chat_id", "community_id", "post_id") VALUES($1, $2, $3) '
                                'RETURNING "chat_id", "community_id", "post_id";',
                                int(communities[num]['id']), int(posts['owner_id']), int(posts['id'])
                            ))
                        time.sleep(1)
                    except Exception as e:
                        logging.error("Exception has been occurred while trying to send message to the channel.",
                                      exc_info=True)
                        continue
            time.sleep(900)
        except Exception as e:
            logging.error("Exception has been occurred while trying to execute the method.", exc_info=True)
            return e

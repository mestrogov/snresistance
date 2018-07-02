# -*- coding: utf-8 -*-


from app import logging
from app import config as config
from app.bot import bot as bot
from app.utils.post_statistics import statistics as postStatistics
from app.remote.postgresql import Psql as psql
from telebot import types
from operator import itemgetter
from ast import literal_eval
import logging
import asyncio
import requests
import time


def polling():
    while True:
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            communities = loop.run_until_complete(psql.fetch(
                'SELECT id, owner_id, community_id FROM channels;',
            ))

            time.sleep(1)

            for num in range(len(communities)):
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
                                          "v": "5.78"
                                      })

                posts_original = posts.json()['response']
                posts = posts.json()['response']['items']

                for pnum in range(len(posts)):
                    is_posted = loop.run_until_complete(psql.fetchrow(
                        'SELECT post_id FROM posts WHERE chat_id = $1 AND community_id = $2 AND post_id = $3;',
                        int(communities[num]['id']), int(posts[pnum]['owner_id']), int(posts[pnum]['id'])
                    ))

                    try:
                        if is_posted:
                            continue
                    except:
                        pass

                    try:
                        if str(posts[pnum]['marked_as_ads']) == "1":
                            continue
                    except:
                        pass

                    if not config.developerMode:
                        loop.run_until_complete(psql.execute(
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

                    attachments = None
                    photos = None
                    videos = None
                    audios = None
                    links = None

                    try:
                        try:
                            # noinspection PyStatementEffect
                            posts[pnum]['attachments']

                            attachments = True
                            photos = []
                            videos = []
                            audios = []
                            links = []

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
                                    time.sleep(1)
                                elif posts[pnum]['attachments'][anum]['type'] == "audio":
                                    audios.extend([{"artist": str(posts[pnum]['attachments'][anum]['audio']['artist']),
                                                    "title": str(posts[pnum]['attachments'][anum]['audio']['title'])}])
                                elif posts[pnum]['attachments'][anum]['type'] == "link":
                                    links.extend([{"title": str(posts[pnum]['attachments'][anum]['link']['title']),
                                                   "url": str(posts[pnum]['attachments'][anum]['link']['url'])}])
                        except KeyError:
                            logging.debug("There is no attachments in this post: " + str(posts[pnum]['owner_id']) +
                                          "_" + str(posts[pnum]['id']) + ".")
                    except Exception as e:
                        logging.error("Exception has been occurred while trying to execute the method.",
                                      exc_info=True)

                    # SELECT id FROM TAG_TABLE WHERE 'aaaaaaaa' LIKE '%' || tag_name || '%';
                    markup, poll = postStatistics(posts=posts[pnum], chat_id=communities[num]['id'], mtype="initiate")

                    template_text = "[Оригинальная публикация во ВКонтакте.](https://vk.com/{0}?w=wall-{1}_{2})" \
                                    "\n\n{3}".format(
                                         posts_original['groups'][0]['screen_name'],
                                         posts_original['groups'][0]['id'],
                                         posts[pnum]['id'],
                                         posts[pnum]['text']
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
                                                 "search?q={1} {2}) — SoundCloud".format(
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

                    # channel.fix_markdown(posts[pnum]['text']))
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
                    time.sleep(1.25)
            time.sleep(900)
        except Exception as e:
            logging.error("Exception has been occurred while trying to execute the method.", exc_info=True)
            return e


"""
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
"""

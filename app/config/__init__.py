# -*- coding: utf-8 -*-

from os import getenv
from sys import exit
import logging

# dae167abbd450adabe7fe1c1c79c13f6a05c6b92f033b040881a0bcc2989c438ae4a7b3aa531b1b6420e2 ; 168313418
try:
    botToken = getenv("SNRESISTANCE_TOKEN", "575841584:AAGzsHDs7ww-q3KvtC2QngJnRrBmgBj7blM")
    developerMode = getenv("SNRESISTANCE_DEVMODE", True)

    # Database Credentials
    databaseHost = getenv("POSTGRES_HOST", "127.0.0.1")
    databasePort = getenv("POSTGRES_PORT", 5432)
    databaseName = getenv("POSTGRES_DB", "SNResistance")
    databaseUsername = getenv("POSTGRES_USERNAME", "SNResistance")

    # Redis Credentials
    redisHost = getenv("REDIS_HOST", "127.0.0.1")
    redisPort = getenv("REDIS_PORT", 6379)
except (KeyError, IndexError):
    logging.critical("Exception has been occurred while trying to get environment variables.", exc_info=True)
    exit(1)

startMessage = \
    "*Cоциальные сети* — абсолютное зло из 2004 года, с тех пор они не видоизменились и не поменяли своей сути." \
    "\n\n"\
    "На моей памяти существует множество людей, которые хотели отказаться от социальных сетей, но не могли из-за одной их прекрасной возможности — сообществ. " \
    "В Telegram для их замены существуют каналы, но далеко не у каждого сообщества он есть (а если и есть, то в большинстве случаев посты появляются позже). Я столкнулся с такой же ситуацией в прошлом, поэтому сейчас и существует этот Бот, " \
    "который в этом хорошем деле поможет[.](http://telegra.ph/Otkaz-ot-polzovaniya-socialnymi-setyami-06-05) " \
    "[Советую также подписаться на мой канал](https://t.me/paparazziBarbos), в нем публикуются предложенные Вами посты, мои мысли, " \
    "репосты из других источников, картинки и вообще все, что реально годно." \
    "\n\n" \
    "Бот работает в данный момент только с сообществами ВКонтакте. Ниже перечислены основные его возможности, которые помогут отказаться от социальных сетей:" \
    "\n" \
    "   - Вы можете задать Боту сообщества, из которых хотите получать репосты новых публикаций." \
    "\n" \
    "   - Два раза в день Вы получаете подборку самых лучших публикаций из сообществ, на которые подписаны." \
    "\n\n" \
    "Более подробно обо мне можете прочитать [здесь](http://telegra.ph/Otkaz-ot-polzovaniya-socialnymi-setyami-06-05)."

channelDescription = "Неофициальный Канал сообщества, созданный одним из пользователей @SNResistanceBot"

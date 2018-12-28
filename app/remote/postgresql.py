# -*- coding: utf-8 -*-

from app import logging
from app import config
import logging
import asyncpg


class Psql:
    @staticmethod
    async def connection():
        try:
            psql_connection = await asyncpg.connect(host=config.databaseHost,
                                                    database=config.databaseName,
                                                    user=config.databaseUsername,
                                                    port=config.databasePort)

            logging.info("Соединение с Базой Данных PostgreSQL может быть установлено успешно.")
            logging.debug("Returned response: " + str(psql_connection))

            await psql_connection.close()
            return "OK"
        except Exception as e:
            logging.error("Произошла ошибка при попытке подключения к Базе Данных PostgreSQL.", exc_info=True)
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
            logging.error("Произошла ошибка при попытке выполнения SQL запроса.", exc_info=True)
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
            # Результат может быть удобно парсирован так: result[0]['COLUMN']
            return result
        except Exception as e:
            logging.error("Произошла ошибка при попытке получения данных из PostgreSQL.", exc_info=True)
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
            logging.error("Произошла ошибка при попытке получения линии (fetch row) данных из PostgreSQL.",
                          exc_info=True)
            return e

    @staticmethod
    async def create_tables():
        try:
            await Psql.execute(
                'CREATE TABLE IF NOT EXISTS "public"."channels" ("chat_id" bigint, "community_id" int NOT NULL, '
                '"owner_id" int NOT NULL, "access_token" text NOT NULL, "channel_link" text NOT NULL, '
                'PRIMARY KEY ("chat_id"), UNIQUE ("community_id"), UNIQUE ("channel_link"));'
            )

            logging.debug("Таблица channels была успешно создана в PostgreSQL.")
            return "OK"
        except Exception as e:
            logging.error("Произошла ошибка при попытке создания таблиц в PostgreSQL.", exc_info=True)
            return e

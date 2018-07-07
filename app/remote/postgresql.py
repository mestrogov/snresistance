# -*- coding: utf-8 -*-

from app import logging
from app import config
import logging
import asyncpg


class Psql:
    @staticmethod
    async def connection():
        try:

            response = await Psql.fetchrow("SELECT pong FROM ping WHERE pong = TRUE;")

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

    @staticmethod
    async def create_tables():
        try:
            try:
                await Psql.execute(
                    'CREATE TABLE IF NOT EXISTS "public"."ping" ("pong" boolean DEFAULT true, PRIMARY KEY ("pong"));'
                )
            except Exception as e:
                logging.critical("Couldn't create table ping.", exc_info=True)
                return e

            try:
                await Psql.execute(
                    'CREATE TABLE IF NOT EXISTS "public"."users" ("id" int, "admin" boolean NOT NULL DEFAULT false, '
                    '"paid_account" boolean NOT NULL DEFAULT false, "communities" text, "access_token" text, '
                    'PRIMARY KEY ("id"));'
                )
            except Exception as e:
                logging.critical("Couldn't create table users.", exc_info=True)
                return e

            try:
                await Psql.execute(
                    'CREATE TABLE IF NOT EXISTS "public"."channels" ("id" bigint, "owner_id" int NOT NULL, '
                    '"community_id" int NOT NULL, PRIMARY KEY ("id"));'
                )
            except Exception as e:
                logging.critical("Couldn't create table channels.", exc_info=True)
                return e

            try:
                await Psql.execute(
                    'CREATE TABLE IF NOT EXISTS "public"."posts" ("chat_id" bigint NOT NULL, "message_id" int '
                    'NOT NULL, "community_id" int NOT NULL, "post_id" int NOT NULL);'
                )
            except Exception as e:
                logging.critical("Couldn't create table posts.", exc_info=True)
                return e

            logging.info("All missing tables were created successfully (if there were any).")

            return "OK"
        except Exception as e:
            logging.error("Exception has been occurred while trying to create tables in the PostgreSQL "
                          "database.", exc_info=True)
            return e

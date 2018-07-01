# -*- coding: utf-8 -*-

from app import logging
from app import config
import logging
import aioredis


class Redis:
    @staticmethod
    async def connection():
        try:
            response = await Redis.execute("ping")

            logging.info("The connection to Redis Server can be established successfully.")
            logging.debug("Returned response: " + str(response))
            return "OK"
        except Exception as e:
            logging.error("Exception has been occurred while trying to establish connection with "
                          "Redis.", exc_info=True)
            return e

    @classmethod
    async def execute(cls, *args):
        try:
            logging.debug("Passed arguments: " + str(args))

            redis_connection = await aioredis.create_connection(
                (config.redisHost, config.redisPort), encoding="UTF-8")

            result = await redis_connection.execute(*args, encoding="UTF-8")
            redis_connection.close()
            await redis_connection.wait_closed()
            return result
        except Exception as e:
            logging.error("Exception has been occurred while trying to execute Redis statement.", exc_info=True)
            return e

import logging

import asyncio
from app.request_handler import ExternalRequestHandler


logger = logging.getLogger("app")


class DataHandler:
    request_handler = ExternalRequestHandler()

    SERVICES_URL = ""

    BLOB_STORAGE_SERVICE_NAME = ""
    STORAGE_BUCKET_NAME = ""

    DB_SERVICE_NAME = ""
    DB_TABLE_NAME = ""

    CACHE_TIMEOUT = 5 * 60  # seconds

    cleanup_triggered = True

    async def _periodical_cleanup(self):
        """
        Periodically (self.CACHE_TIMEOUT) clean up the data
        """
        while self.cleanup_triggered:
            await asyncio.sleep(self.CACHE_TIMEOUT)
            logger.info("Periodical cleanup started.")
            await self.cleanup_old_cached_data()
            logger.info("Periodical cleanup completed.")

    @classmethod
    def teardown_class(cls):
        cls.cleanup_triggered = False

    async def fetch_weather(self, city: str):
        """
        Method called in API to fetch weather data
        :param city: city name
        :return: dict with weather data
        """
        if cached := await self.check_cached_data(city):
            city = city.lower()
            logger.info(f"Found cached weather data for: {city}")
            return cached
        if (response_json := await self.fetch_weather_api(city)).get("ok"):
            logging.info(f"Successfully fetched weather data for: {city}")
            storage_data = await self.store_data(city, response_json)
            await self.log_data(city, storage_data.get("path", ""))
            logging.info(f"Successfully stored and logged weather data for {city}")
        return response_json

    async def fetch_weather_api(self, city: str) -> dict:
        return await self.request_handler.get_weather(city)

    async def store_data(self, city: str, data: dict):
        """
        On successful request from weather API it is required to store data as file
        :param city: city name
        :param data: data to be stored
        """
        raise NotImplementedError()

    async def check_cached_data(self, city: str) -> dict:
        """
        Before making request to weather API, it is required to check cached data
        :param city: city name
        :return: cached data
        """
        raise NotImplementedError()

    async def log_data(self, city: str, data: dict):
        """
        On successful request to weather API and store of data as file log in database is required
        :param city: city name
        :param data: additional data to be logged
        """
        raise NotImplementedError()

    async def ensure_database_table_exists(self, table_name: str):
        """
        Database table must exist before attempt to send anything into it
        :param table_name: table name of database table
        """
        raise NotImplementedError()

    async def ensure_bucket_exists(self, bucket_name: str):
        """
        Bucket of blob storage must exist before attempt to send anything into it
        :param bucket_name: name of bucket in blob storage
        """
        raise NotImplementedError()

    async def cleanup_old_cached_data(self):
        """
        Cleanup old cached data is required for self.CACHE_TIMEOUT period
        """
        raise NotImplementedError()

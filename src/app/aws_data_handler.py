import json
import datetime
import logging

from aioboto3 import Session

import settings
from app.data_handler import DataHandler


logger = logging.getLogger("app")


class AWSDataHandler(DataHandler):
    SERVICES_URL = settings.SERVICES_URL
    SERVICE_REGION = settings.SERVICE_REGION

    BLOB_STORAGE_SERVICE_NAME = "s3"
    STORAGE_BUCKET_NAME = settings.STORAGE_BUCKET_NAME

    DB_SERVICE_NAME = "dynamodb"
    DB_TABLE_NAME = settings.DB_TABLE_NAME

    def __init__(self):
        super().__init__()
        self.session = None
        self.api_access_key = settings.SERVICE_ACCESS_KEY or None
        self.api_secret_key = settings.SERVICE_ACCESS_KEY_SECRET or None
        self.region_name = settings.SERVICE_REGION

    def ensure_session(self, session = None) -> Session:
        """
        Create or return aioboto3 Session
        :param session: if needed can be passed. Defaults to None
        :return: session object
        """
        if session:
            self.session = session
        if not self.session:
            self.session = Session(
                aws_access_key_id=self.api_access_key,
                aws_secret_access_key=self.api_secret_key,
                region_name=self.region_name
            )
        return self.session


    async def store_data(self, city, data) -> dict:
        """
        Stores data in S3 storage
        :param city: city name
        :param data: data to store
        :return: dict containing path of the file for the S3
        """
        name = f"{city}_{datetime.datetime.now().isoformat()}.json"
        async with self.ensure_session().resource(self.BLOB_STORAGE_SERVICE_NAME, endpoint_url=self.SERVICES_URL) as s3:
            bucket = await s3.Bucket(self.STORAGE_BUCKET_NAME)
            await bucket.put_object(Key=name, Body=json.dumps(data))
            logger.info(f"Stored {name} in s3 storage")
            return {"path": f"s3://{self.STORAGE_BUCKET_NAME}/{name}"}

    async def check_cached_data(self, city) -> dict:
        """
        Checks file in S3 storage.
        :param city: city name
        :return: downloaded data from S3
        """
        async with self.ensure_session().resource(self.BLOB_STORAGE_SERVICE_NAME, endpoint_url=self.SERVICES_URL) as s3:
            bucket = await s3.Bucket(self.STORAGE_BUCKET_NAME)
            async for file in bucket.objects.filter(Prefix=city):
                if not await self._is_within_timeout(file.key):
                    continue
                obj = await s3.Object(self.STORAGE_BUCKET_NAME, file.key)
                file_data = await obj.get()
                downloaded_data = json.loads((await file_data['Body'].read()).decode('utf-8'))
                return downloaded_data

    async def _is_within_timeout(self, filename: str) -> bool:
        """
        Checks whether a file exists within a certain time period.
        :param filename: name of the file to check
        :return: True if file exists and within a certain time period
        """
        _, timestamp = filename.split('_')
        timestamp = timestamp.split('.')[0]
        dt = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S")
        return (datetime.datetime.now() - dt) <= datetime.timedelta(seconds=self.CACHE_TIMEOUT)

    async def log_data(self, city, path: str):
        """
        Sends data to DynamoDB
        :param city: city name
        :param path: path as table data
        """
        async with self.ensure_session().resource(self.DB_SERVICE_NAME, endpoint_url=self.SERVICES_URL) as db_client:
            table = await db_client.Table(self.DB_TABLE_NAME)
            await table.put_item(Item={
                'city': city,
                "timestamp": str(datetime.datetime.now().isoformat()),
                "url": path or "",
            })

    async def ensure_database_table_exists(self, table_name: str):
        logger.info("Ensuring database table exists")
        async with self.ensure_session().resource(self.DB_SERVICE_NAME, endpoint_url=self.SERVICES_URL) as db_client:
            table = await db_client.Table(table_name)
            try:
                await table.load()
            except Exception as e:
                logger.info("Table does not exist, creating it")
                table = await db_client.create_table(
                    TableName=table_name,
                    KeySchema=[
                        {"AttributeName": "city", "KeyType": "HASH"},
                        {"AttributeName": "timestamp", "KeyType": "RANGE"},
                    ],
                    AttributeDefinitions=[
                        {"AttributeName": "city", "AttributeType": "S"},
                        {"AttributeName": "timestamp", "AttributeType": "S"},
                    ],
                    ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
                )
                await table.wait_until_exists()
                logger.info("Database table created")

    async def ensure_bucket_exists(self, bucket_name: str):
        logger.info("Ensuring bucket exists")
        async with self.ensure_session().resource(self.BLOB_STORAGE_SERVICE_NAME, endpoint_url=self.SERVICES_URL) as s3:
            async for bucket in s3.buckets.all():
                if bucket.name == bucket_name:
                    logger.info("Bucket exists")
                    return
            bucket = await s3.create_bucket(Bucket=bucket_name)
            await bucket.wait_until_exists()
            logger.info("Bucket created")

    async def cleanup_old_cached_data(self):
        """
        Removes cached data from S3 if expired.
        """
        logger.info("Cleaning up old cached data")
        async with self.ensure_session().resource(self.BLOB_STORAGE_SERVICE_NAME, endpoint_url=self.SERVICES_URL) as s3:
            bucket = await s3.Bucket(self.STORAGE_BUCKET_NAME)
            async for file in bucket.objects.all():
                if await self._is_within_timeout(file.key):
                    continue
                logger.debug(f"Deleting {file.key}")
                await file.delete()

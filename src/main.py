import asyncio
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

import constants
import settings
from app.data_handler import DataHandler


handler: DataHandler = constants.HANDLERS[settings.SERVICE_HANDLER_NAME]()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await asyncio.gather(
        handler.ensure_database_table_exists(handler.DB_TABLE_NAME),
        handler.ensure_bucket_exists(handler.STORAGE_BUCKET_NAME)
    )
    asyncio.create_task(handler._periodical_cleanup())
    yield
    handler.teardown_class()

app = FastAPI(lifespan=lifespan)

async def cleanup_cache_data():
    await handler.cleanup_cache_data()

@app.get("/weather")
async def weather(city: str):
    return await handler.fetch_weather(city)

if __name__ == "__main__":
    uvicorn.run(
        app,
        host=settings.API_HOST,
        port=int(settings.API_PORT),
        log_level=settings.LOG_LEVEL.lower(),
        log_config=settings.LOGGING_CONFIG,
    )
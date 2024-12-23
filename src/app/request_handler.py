import aiohttp
import logging

import settings
import constants


logger = logging.getLogger("app")


class ExternalRequestHandler:
    async def get_weather(self, city):
        params = {
            "q": city,
            "appid": settings.WEATHER_API_KEY,
        }
        logger.info(f"Making request to external API for: {city}")
        async with aiohttp.ClientSession() as session:
            async with session.get(url=f"{constants.BASE_URL}{constants.WEATHER_EP}", params=params) as response:
                logger.info(f"Got response from external API")
                return await self.handle_response(await response.json())

    async def handle_response(self, response_json: dict):
        """
        Handles response from weather API
        :param response_json: Response json form weather API
        :return: Formatted response from weather with added `ok` key to signal is response actually ok
        """
        response_json["code"] = response_json.get("code") or response_json.pop("cod", None)
        if response_json.get("code") != 200:
            response_json["ok"] = False
        else:
            response_json["ok"] = True
        return response_json
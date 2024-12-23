from app.aws_data_handler import AWSDataHandler

HANDLERS = {
    "aws": AWSDataHandler,
}

BASE_URL = "https://api.openweathermap.org/"
WEATHER_EP = "data/2.5/weather"
import os


SERVICES_URL = os.environ.get("SERVICES_URL", None)
SERVICE_ACCESS_KEY = os.environ.get("SERVICE_ACCESS_KEY", "test")
SERVICE_ACCESS_KEY_SECRET = os.environ.get("SERVICE_ACCESS_KEY_SECRET", "test")
SERVICE_HANDLER_NAME = os.environ.get("SERVICE_HANDLER_NAME")
SERVICE_REGION = os.environ.get("SERVICE_REGION", "us-east-1")


# storage
STORAGE_BUCKET_NAME = os.environ.get("STORAGE_BUCKET_NAME", "")
DB_TABLE_NAME = os.environ.get("DB_TABLE_NAME", "")


# weather api
WEATHER_API_KEY = os.environ.get("WEATHER_API_KEY", "")

# fastAPI
API_HOST = os.environ.get("API_HOST", "0.0.0.0")
API_PORT = os.environ.get("API_PORT", "8000")
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
        'custom_formatter': {
            'format': "%(asctime)s [%(processName)s: %(process)d] [%(threadName)s: %(thread)d] [%(levelname)s] %(message)s"

        },
    },
    'handlers': {
        'default': {
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',  # Default is stderr
        },
        'stream_handler': {
            'formatter': 'custom_formatter',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',  # Default is stderr
        },
        'file_handler': {
            'formatter': 'custom_formatter',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'app.log',
            'maxBytes': 1024 * 1024 * 10,  # = 10MB
            'backupCount': 3,
        },
    },
    'loggers': {
        'app': {
            'handlers': ['default', 'file_handler'],
            'level': LOG_LEVEL,
            'propagate': False,
        },
        'uvicorn': {
            'handlers': ['default', 'file_handler'],
            'level': 'TRACE',
            'propagate': False
        },
        'uvicorn.access': {
            'handlers': ['stream_handler', 'file_handler'],
            'level': 'TRACE',
            'propagate': False
        },
        'uvicorn.error': {
            'handlers': ['stream_handler', 'file_handler'],
            'level': 'TRACE',
            'propagate': False
        },
        'uvicorn.asgi': {
            'handlers': ['stream_handler', 'file_handler'],
            'level': 'TRACE',
            'propagate': False
        },

    },
}
import dj_database_url

from .base import *
from decouple import config


SECRET_KEY = config("SECRET_KEY")

DEBUG = config("DEBUG", default=False, cast=bool)

ALLOWED_HOSTS = config("ALLOWED_HOSTS").split(",")

DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL'),
        conn_max_age=60,
        ssl_require=True,
    )
}

REDIS_URL= config("REDIS_URL")
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": config("REDIS_URL"),
    }
}


CORS_ALLOWED_ORIGINS = [
    "https://quantumways-api-staging.onrender.com"
    "http://localhost:8000",  # or the frontend URL
    "http://127.0.0.1:5500",  # or the frontend URL
]
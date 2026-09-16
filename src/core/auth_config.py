from datetime import timedelta

from authx import AuthX, AuthXConfig

from src.core.config import settings

# Настройка AuthX строго на Хедеры (Bearer Token)
config = AuthXConfig()
config.JWT_SECRET_KEY = settings.SECRET_KEY
config.JWT_TOKEN_LOCATION = ["headers"]
config.JWT_HEADER_NAME = "Authorization"
config.JWT_HEADER_TYPE = "Bearer"
config.JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=1)

security = AuthX(config=config)


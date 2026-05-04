import logging
import os
from pathlib import Path

from pydantic import Field, ValidationError
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)

BASE_DIR = Path(__file__).resolve().parent.parent


class LoggingSettings(BaseSettings):
    """Настройки логирования"""

    LOG_LEVEL: int = logging.INFO
    DATE_FORMAT: str = "%Y-%m-%d %H:%M:%S"
    LOG_FORMAT: str = (
        "[%(asctime)s.%(msecs)03d] %(module)10s:%(lineno)-3d %(levelname)-7s - %(message)s"
    )
    LOG_FILE: str = "logs/app.log"

    def setup(self) -> None:
        # Обеспечиваем существование директории для логов
        log_dir = os.path.dirname(self.LOG_FILE)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)

        logging.basicConfig(
            level=self.LOG_LEVEL,
            format=self.LOG_FORMAT,
            datefmt=self.DATE_FORMAT,
            handlers=[
                logging.FileHandler(self.LOG_FILE),
                logging.StreamHandler(),
            ],
        )


class DatabaseSettings(BaseSettings):
    """Настройки PostgreSQL"""

    DB_USER: str = "user"
    DB_PASSWORD: str = "password"
    DB_HOST: str = "db"
    DB_PORT: int = 5432
    DB_NAME: str = "sfmshop"

    def get_sqlalchemy_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@"
            f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    def get_asyncpg_url(self) -> str:
        return (
            f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@"
            f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )


class MongoSettings(BaseSettings):
    """Настройки MongoDB"""

    MONGO_URL: str = "mongodb://localhost:27017/"
    MONGO_DB_NAME: str = "sfmshop_logs"


class AuthSettings(BaseSettings):
    """Настройки аутентификации"""

    SECRET_KEY: str = "my-secret-key"
    ALGORITHM: str = "HS256"
    UNSAFE_METHODS: frozenset[str] = frozenset({"POST", "PUT", "PATCH", "DELETE"})


class APIAccessSettings(BaseSettings):
    """Настройки доступа к API"""

    API_TOKENS: frozenset[str] = frozenset(
        {
            "lQOWvNaVMuWtCbiUPIJ9YQ",
            "DVYBiDolEXzREsZ9VygBEA",
            "aOnysL02BttFNWZv_gkvPg",
        }
    )


class ExternalServicesSettings(BaseSettings):
    """Настройки внешних сервисов"""

    ANTHROPIC_API_KEY: str = Field(default="", description="API key для Anthropic")


class Settings(BaseSettings):
    """Корневой класс настроек — объединяет все группы"""

    logging: LoggingSettings = Field(default_factory=LoggingSettings)
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    mongo: MongoSettings = Field(default_factory=MongoSettings)
    auth: AuthSettings = Field(default_factory=AuthSettings)
    api_access: APIAccessSettings = Field(default_factory=APIAccessSettings)
    external: ExternalServicesSettings = Field(default_factory=ExternalServicesSettings)

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env"),
        env_nested_delimiter="__",
        extra="allow",
    )

    def setup_logging(self) -> None:
        self.logging.setup()


try:
    settings = Settings()
    settings.setup_logging()
except ValidationError:
    raise

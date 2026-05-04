import logging

from core.config import settings


class LogService:
    """Сервис логирования"""

    def __init__(
        self,
        log_file: str = "app.log",
    ):
        logging.basicConfig(
            level=settings.logging.LOG_LEVEL,
            format=settings.logging.LOG_FORMAT,
            datefmt=settings.logging.DATE_FORMAT,
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(),
            ],
        )
        logging.getLogger("watchfiles").setLevel(logging.WARNING)
        logging.getLogger("watchfiles.main").setLevel(logging.WARNING)
        self.logger = logging.getLogger(__name__)
        self.logger.propagate = False

    def info(self, msg: str, **kwargs) -> None:
        """Уровень инфо"""
        self.logger.info(msg, extra=kwargs)

    def error(self, msg: str, **kwargs) -> None:
        """Уровень error"""
        self.logger.error(msg, extra=kwargs)

    def warning(self, msg: str, **kwargs) -> None:
        """Ур warning"""
        self.logger.warning(msg, extra=kwargs)

    def critical(self, msg: str, **kwargs) -> None:
        """Уровень critical"""
        self.logger.critical(msg, extra=kwargs)

    def debug(self, msg: str, **kwargs) -> None:
        """Уровень debug"""
        self.logger.debug(msg, extra=kwargs)

    def exception(self, msg: str, **kwargs) -> None:
        """Уровень exception"""
        self.logger.exception(msg, extra=kwargs)

    # объект логирования сообщений


log_service = LogService()

import logging


class LogService:
    """Сервис логирования для проекта SFMShop"""

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)

    def info(self, message: str, **kwargs):
        """Логирование информационного сообщения"""
        self.logger.info(f"{message} | {kwargs}")

    def error(self, message: str, **kwargs):
        """Логирование ошибки"""
        self.logger.error(f"{message} | {kwargs}")

    def warning(self, message: str, **kwargs):
        """Логирование предупреждения"""
        self.logger.warning(f"{message} | {kwargs}")

    def critical(self, message: str, **kwargs):
        """Логирование критической ошибки"""
        self.logger.critical(f"{message} | {kwargs}")


log_service = LogService()

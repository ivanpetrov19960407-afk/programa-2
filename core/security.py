from __future__ import annotations

import logging
from typing import Optional

import keyring


class SecurityService:
    \"\"\"Сервис безопасного хранения секретов через системный keyring.\"\"\"

    def __init__(self, app_prefix: str = \"UniversalAI_Assistant_\") -> None:
        self._app_prefix = app_prefix
        self._logger = logging.getLogger(self.__class__.__name__)

    def store_secret(self, key: str, value: str) -> bool:
        \"\"\"Сохраняет секрет с префиксом приложения.\"\"\"
        storage_key = f\"{self._app_prefix}{key}\"
        try:
            keyring.set_password(self._app_prefix, storage_key, value)
            return True
        except Exception:
            self._logger.exception(\"Не удалось сохранить секрет: %s\", storage_key)
            return False

    def get_secret(self, key: str) -> Optional[str]:
        \"\"\"Возвращает секрет по ключу или None при ошибке.\"\"\"
        storage_key = f\"{self._app_prefix}{key}\"
        try:
            return keyring.get_password(self._app_prefix, storage_key)
        except Exception:
            self._logger.exception(\"Не удалось получить секрет: %s\", storage_key)
            return None

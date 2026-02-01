from __future__ import annotations

import os
from typing import AsyncGenerator, List, Optional

from litellm import acompletion

from core.security import SecurityService


class AiInferenceEngine:
    \"\"\"Движок для работы с LLM через litellm.\"\"\"

    def __init__(self, security_service: SecurityService, use_vpn: bool = False) -> None:
        self._security_service = security_service
        self.use_vpn = use_vpn

    def _configure_proxy(self) -> None:
        \"\"\"Настраивает переменные окружения для прокси.\"\"\"
        if self.use_vpn:
            proxy_value = \"socks5://127.0.0.1:1080\"
            os.environ[\"HTTP_PROXY\"] = proxy_value
            os.environ[\"HTTPS_PROXY\"] = proxy_value
            os.environ[\"ALL_PROXY\"] = proxy_value
            return
        for key in (\"HTTP_PROXY\", \"HTTPS_PROXY\", \"ALL_PROXY\"):
            os.environ.pop(key, None)

    def _resolve_api_key(self, model: str) -> Optional[str]:
        \"\"\"Выбирает API ключ в зависимости от модели.\"\"\"
        normalized = model.lower()
        if \"gpt\" in normalized or \"openai\" in normalized:
            return self._security_service.get_secret(\"openai_api_key\")
        if \"claude\" in normalized or \"anthropic\" in normalized:
            return self._security_service.get_secret(\"anthropic_api_key\")
        return None

    async def generate_response_stream(
        self, model: str, messages: List[dict]
    ) -> AsyncGenerator[str, None]:
        \"\"\"Асинхронный генератор ответа от модели.\"\"\"
        self._configure_proxy()
        api_key = self._resolve_api_key(model)
        stream = await acompletion(model=model, messages=messages, stream=True, api_key=api_key)
        async for chunk in stream:
            delta = chunk.get(\"choices\", [{}])[0].get(\"delta\", {})
            token = delta.get(\"content\", \"\")
            if token:
                yield token

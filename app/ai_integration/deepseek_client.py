"""Обёртка над DeepSeek API."""
from typing import List, Dict
import openai
from config.settings import config

class AIService:
    def __init__(self) -> None:
        self._client = openai.AsyncOpenAI(
            api_key=config.ai.api_key,
            base_url=config.ai.base_url
        )

    async def chat(self, messages: List[Dict[str, str]]) -> str:
        response = await self._client.chat.completions.create(
            model=config.ai.model,
            messages=messages,
            max_tokens=config.ai.max_tokens,
            temperature=config.ai.temperature
        )
        return response.choices[0].message.content

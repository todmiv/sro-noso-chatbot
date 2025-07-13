"""Обновленный клиент DeepSeek с использованием нативного SDK."""
from typing import List, Dict, Optional
import asyncio

from config.settings import config
from app.ai_integration.deepseek_sdk import DeepSeekClient as NativeDeepSeekClient, DeepSeekError


class DeepSeekClient:
    """Обёртка над нативным DeepSeek клиентом для обратной совместимости."""
    
    def __init__(self):
        self._client = NativeDeepSeekClient(
            api_key=config.ai.api_key,
            model=config.ai.model,
            timeout=30,
            max_retries=3,
            cache_ttl=3600
        )
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = None,
        max_tokens: int = None,
        temperature: float = None
    ) -> str:
        """Выполняет запрос к DeepSeek API."""
        try:
            response = await self._client.chat_completion(
                messages=messages,
                model=model or config.ai.model,
                max_tokens=max_tokens or config.ai.max_tokens,
                temperature=temperature or config.ai.temperature
            )
            return response.content
            
        except DeepSeekError as e:
            raise Exception(f"DeepSeek API error: {e}")
    
    async def generate_response(
        self,
        user_question: str,
        context: Optional[str] = None,
        system_prompt: Optional[str] = None
    ) -> str:
        """Генерирует ответ на вопрос пользователя."""
        messages = []
        
        # Системный промпт
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        else:
            default_prompt = (
                "Ты консультант СРО НОСО. Отвечай точно и профессионально на вопросы "
                "по строительной деятельности и документам СРО. Используй только "
                "предоставленную информацию."
            )
            messages.append({"role": "system", "content": default_prompt})
        
        # Контекст из документов
        if context:
            messages.append({
                "role": "system", 
                "content": f"Информация из документов СРО:\n{context}"
            })
        
        # Вопрос пользователя
        messages.append({"role": "user", "content": user_question})
        
        return await self.chat_completion(messages)
    
    async def close(self) -> None:
        """Закрывает клиент."""
        await self._client.close()

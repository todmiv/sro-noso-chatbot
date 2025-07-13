import asyncio
import time
import json
import httpx
import hashlib
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


class DeepSeekError(Exception):
    """Исключение для ошибок DeepSeek API."""
    pass


@dataclass
class DeepSeekResponse:
    """Ответ от DeepSeek API."""
    content: str
    model: str
    usage: Dict[str, int]
    finish_reason: str


class DeepSeekClient:
    """Нативный клиент для DeepSeek API."""
    
    BASE_URL = "https://api.deepseek.com/v1"
    
    def __init__(
        self,
        api_key: str,
        model: str = "deepseek-chat",
        timeout: int = 30,
        max_retries: int = 3,
        cache_ttl: int = 3600
    ):
        self.api_key = api_key
        self.model = model
        self.timeout = timeout
        self.max_retries = max_retries
        self.cache_ttl = cache_ttl
        
        # Простой in-memory кэш
        self._cache: Dict[str, Tuple[float, DeepSeekResponse]] = {}
        
        # HTTP клиент
        self._client = httpx.AsyncClient(
            timeout=self.timeout,
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
        )
    
    def _get_cache_key(self, messages: List[Dict], model: str) -> str:
        """Создает ключ кэша для запроса."""
        content = json.dumps(messages, sort_keys=True) + model
        return hashlib.md5(content.encode()).hexdigest()
    
    def _get_from_cache(self, cache_key: str) -> Optional[DeepSeekResponse]:
        """Получает ответ из кэша."""
        if cache_key in self._cache:
            timestamp, response = self._cache[cache_key]
            if time.time() - timestamp < self.cache_ttl:
                logger.debug(f"Cache hit for key {cache_key[:8]}...")
                return response
            else:
                # Удаляем устаревший кэш
                del self._cache[cache_key]
        return None
    
    def _save_to_cache(self, cache_key: str, response: DeepSeekResponse) -> None:
        """Сохраняет ответ в кэш."""
        self._cache[cache_key] = (time.time(), response)
        logger.debug(f"Cached response for key {cache_key[:8]}...")
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        stream: bool = False
    ) -> DeepSeekResponse:
        """Выполняет запрос к DeepSeek API."""
        
        used_model = model or self.model
        cache_key = self._get_cache_key(messages, used_model)
        
        # Проверяем кэш
        if not stream:  # Для stream запросов кэш не используем
            cached_response = self._get_from_cache(cache_key)
            if cached_response:
                return cached_response
        
        # Подготавливаем запрос
        payload = {
            "model": used_model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Выполняем запрос с повторами
        last_exception = None
        for attempt in range(self.max_retries):
            try:
                response = await self._client.post(
                    f"{self.BASE_URL}/chat/completions",
                    json=payload,
                    headers=headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    deepseek_response = DeepSeekResponse(
                        content=data["choices"][0]["message"]["content"],
                        model=data["model"],
                        usage=data.get("usage", {}),
                        finish_reason=data["choices"][0]["finish_reason"]
                    )
                    
                    # Сохраняем в кэш только успешные ответы
                    if not stream:
                        self._save_to_cache(cache_key, deepseek_response)
                    
                    return deepseek_response
                
                elif response.status_code == 429:
                    # Rate limit - ждем и повторяем
                    wait_time = 2 ** attempt
                    logger.warning(f"Rate limit hit, waiting {wait_time}s before retry {attempt + 1}")
                    await asyncio.sleep(wait_time)
                    continue
                
                elif response.status_code in [401, 403]:
                    raise DeepSeekError(f"Authentication error: {response.status_code}")
                
                elif response.status_code >= 500:
                    # Серверная ошибка - повторяем
                    logger.warning(f"Server error {response.status_code}, retry {attempt + 1}")
                    await asyncio.sleep(1)
                    continue
                
                else:
                    error_data = response.json() if response.headers.get("content-type", "").startswith("application/json") else {}
                    raise DeepSeekError(f"API error {response.status_code}: {error_data}")
                    
            except httpx.TimeoutException as e:
                last_exception = DeepSeekError(f"Request timeout: {e}")
                logger.warning(f"Timeout on attempt {attempt + 1}")
                await asyncio.sleep(1)
                continue
            
            except httpx.RequestError as e:
                last_exception = DeepSeekError(f"Request error: {e}")
                logger.warning(f"Request error on attempt {attempt + 1}: {e}")
                await asyncio.sleep(1)
                continue
        
        # Если все попытки неудачны
        raise last_exception or DeepSeekError("All retry attempts failed")
    
    async def simple_chat(self, user_message: str, system_prompt: Optional[str] = None) -> str:
        """Упрощенный метод для одиночных сообщений."""
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": user_message})
        
        response = await self.chat_completion(messages)
        return response.content
    
    def clear_cache(self) -> None:
        """Очищает кэш."""
        self._cache.clear()
        logger.info("DeepSeek cache cleared")
    
    async def close(self) -> None:
        """Закрывает HTTP клиент."""
        await self._client.aclose()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

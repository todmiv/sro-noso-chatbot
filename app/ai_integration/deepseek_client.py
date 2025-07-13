from typing import List, Dict, Optional
import openai
import asyncio

from config.settings import config


class DeepSeekClient:
    """Клиент для работы с DeepSeek API."""
    
    def __init__(self):
        self._client = openai.AsyncOpenAI(
            api_key=config.ai.api_key,
            base_url=config.ai.base_url
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
            response = await self._client.chat.completions.create(
                model=model or config.ai.model,
                messages=messages,
                max_tokens=max_tokens or config.ai.max_tokens,
                temperature=temperature or config.ai.temperature
            )
            
            return response.choices[0].message.content
            
        except openai.RateLimitError:
            await asyncio.sleep(1)  # Ждем и повторяем
            return await self.chat_completion(messages, model, max_tokens, temperature)
            
        except Exception as e:
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

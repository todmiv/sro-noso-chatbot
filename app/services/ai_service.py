from typing import List, Dict, Optional
import asyncio
from app.ai_integration.deepseek_client import DeepSeekClient
from app.ai_integration.rag_system import RAGSystem
from app.services.session_service import SessionService
from app.monitoring.metrics import RESPONSE_TIME


class AIService:
    """Сервис для работы с искусственным интеллектом."""
    
    def __init__(self):
        self.deepseek_client = DeepSeekClient()
        self.rag_system = RAGSystem()
        self.session_service = SessionService()
    
    async def generate_consultation_response(
        self, 
        user_question: str, 
        user_id: int,
        context: Optional[str] = None
    ) -> str:
        """Генерирует консультационный ответ."""
        with RESPONSE_TIME.labels(service="ai_consultation").time():
            try:
                # Получаем контекст из документов через RAG
                if not context:
                    context = await self._get_document_context(user_question)
                
                # Получаем историю диалога
                conversation_history = await self.session_service.get_conversation_history(user_id)
                
                # Формируем системный промпт
                system_prompt = self._create_system_prompt()
                
                # Формируем сообщения для ИИ
                messages = self._prepare_messages(
                    user_question=user_question,
                    context=context,
                    conversation_history=conversation_history,
                    system_prompt=system_prompt
                )
                
                # Генерируем ответ
                response = await self.deepseek_client.generate_response(
                    user_question=user_question,
                    context=context,
                    system_prompt=system_prompt
                )
                
                # Сохраняем в историю
                await self.session_service.save_interaction(
                    user_id=user_id,
                    user_message=user_question,
                    bot_response=response,
                    context_used=context[:500] if context else None
                )
                
                return response
                
            except Exception as e:
                return f"❌ Извините, произошла ошибка при обработке вашего запроса: {str(e)}"
    
    async def _get_document_context(self, question: str) -> str:
        """Получает релевантный контекст из документов."""
        try:
            # Инициализируем RAG систему если необходимо
            if not self.rag_system._initialized:
                await self.rag_system.initialize()
            
            # Ищем релевантные документы
            search_results = await self.rag_system.search(question, top_k=3)
            
            if not search_results:
                return ""
            
            # Формируем контекст
            context_parts = []
            for result in search_results:
                context_parts.append(result.get("content", ""))
            
            return "\n\n".join(context_parts)
            
        except Exception as e:
            return ""
    
    def _create_system_prompt(self) -> str:
        """Создает системный промпт для ИИ."""
        return (
            "Ты — профессиональный консультант СРО «Нижегородское объединение строительных организаций» (НОСО). "
            "Твоя задача — предоставлять точные, профессиональные и полезные ответы на вопросы о:\n"
            "• Документах и стандартах СРО\n"
            "• Требованиях к членству и процедурах\n"
            "• Строительных нормах и регламентах\n"
            "• Процедурах контроля качества\n"
            "• Взаимодействии с государственными органами\n\n"
            "Правила ответа:\n"
            "1. Используй только предоставленную информацию из документов СРО\n"
            "2. Если информации недостаточно, честно сообщи об этом\n"
            "3. Отвечай профессионально, но доступно\n"
            "4. Структурируй ответ с помощью разделов и списков\n"
            "5. При необходимости рекомендуй обратиться к специалистам СРО\n"
            "6. Избегай юридических консультаций, рекомендуй обратиться к юристам"
        )
    
    def _prepare_messages(
        self,
        user_question: str,
        context: str,
        conversation_history: List[Dict],
        system_prompt: str
    ) -> List[Dict[str, str]]:
        """Подготавливает сообщения для отправки в ИИ."""
        messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        # Добавляем контекст из документов
        if context:
            messages.append({
                "role": "system",
                "content": f"Информация из документов СРО:\n{context}"
            })
        
        # Добавляем историю диалога (последние 5 сообщений)
        for interaction in conversation_history[-5:]:
            messages.append({"role": "user", "content": interaction["user_message"]})
            messages.append({"role": "assistant", "content": interaction["bot_response"]})
        
        # Добавляем текущий вопрос
        messages.append({"role": "user", "content": user_question})
        
        return messages
    
    async def generate_document_summary(self, document_content: str) -> str:
        """Генерирует краткое содержание документа."""
        try:
            summary_prompt = (
                "Создай краткое содержание следующего документа СРО. "
                "Выдели основные моменты, требования и процедуры. "
                "Ответ должен быть структурированным и не более 500 слов."
            )
            
            response = await self.deepseek_client.generate_response(
                user_question=summary_prompt,
                context=document_content
            )
            
            return response
            
        except Exception as e:
            return f"❌ Ошибка при создании резюме: {str(e)}"
    
    async def check_document_compliance(self, user_input: str, requirements: str) -> str:
        """Проверяет соответствие требованиям СРО."""
        try:
            compliance_prompt = (
                f"Проверь соответствие следующей информации требованиям СРО:\n\n"
                f"Информация для проверки:\n{user_input}\n\n"
                f"Требования СРО:\n{requirements}\n\n"
                f"Дай детальную оценку соответствия и рекомендации по улучшению."
            )
            
            response = await self.deepseek_client.chat_completion([
                {"role": "system", "content": "Ты эксперт по проверке соответствия требованиям СРО."},
                {"role": "user", "content": compliance_prompt}
            ])
            
            return response
            
        except Exception as e:
            return f"❌ Ошибка при проверке соответствия: {str(e)}"

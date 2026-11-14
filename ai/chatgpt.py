"""
Интеграция JARVIS с ChatGPT
"""

import openai
import json
from typing import Dict, List, Optional
from pathlib import Path
import logging


class ChatGPTIntegration:
    """Интеграция с OpenAI ChatGPT для умных ответов."""

    def __init__(self, brain):
        self.brain = brain

        # Чтение из переменных окружения
        self.api_key = brain.config.openai_api_key
        self.model = brain.config.openai_model
        self.max_tokens = brain.config.openai_max_tokens
        self.temperature = brain.config.openai_temperature

        if self.api_key:
            openai.api_key = self.api_key
            self.brain.logger.info(f"OpenAI API инициализирован (модель: {self.model})")
        else:
            self.brain.logger.warning("OpenAI API ключ не найден в переменных окружения")

        self.conversation_history: List[Dict] = []
        self.system_prompt = self._build_system_prompt()

    def _build_system_prompt(self) -> str:
        """Системный промпт для JARVIS."""
        return """Ты - JARVIS, продвинутый AI-ассистент, созданный по образу JARVIS из Iron Man.

Твои характеристики:
- Обращайся к пользователю "сэр" (или как он предпочитает)
- Говори вежливо, профессионально, с лёгким британским акцентом в тексте
- Будь лаконичен, но информативен
- Используй сарказм и тонкий юмор иногда
- Предлагай помощь proactively
- Сохраняй контекст разговора

Ты можешь:
- Управлять компьютером пользователя
- Отвечать на вопросы
- Помогать с задачами
- Анализировать данные
- Делать оптимизации

Отвечай на русском языке, если пользователь не попросит иначе."""

    async def ask(self, question: str, context: Dict = None) -> Dict:
        """Задать вопрос ChatGPT."""
        if not self.api_key:
            return {
                "status": "error",
                "message": "OpenAI API ключ не установлен. Добавьте OPENAI_API_KEY в .env файл"
            }

        try:
            # Обработка контекста системы
            messages = [{"role": "system", "content": self.system_prompt}]

            # Добавление контекста
            if context:
                context_msg = self._format_context(context)
                if context_msg:
                    messages.append({"role": "system", "content": context_msg})

            # Добавление истории разговора
            messages.extend(self.conversation_history[-10:])

            # Добавление текущего вопроса
            messages.append({"role": "user", "content": question})

            # Запрос к API
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
            )

            answer = response.choices[0].message.content

            # Сохранение в историю
            self.conversation_history.append({"role": "user", "content": question})
            self.conversation_history.append({"role": "assistant", "content": answer})

            # Ограничение истории
            if len(self.conversation_history) > 20:
                self.conversation_history = self.conversation_history[-20:]

            return {
                "status": "ok",
                "answer": answer,
                "tokens_used": response.usage.total_tokens
            }

        except openai.error.RateLimitError:
            return {"status": "error", "message": "Превышен лимит запросов OpenAI"}
        except openai.error.APIError as e:
            return {"status": "error", "message": f"API ошибка: {str(e)}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _format_context(self, context: Dict) -> Optional[str]:
        """Форматирование контекста для промпта."""
        parts = []

        if "system_info" in context:
            info = context["system_info"]
            parts.append(f"Система: CPU {info.get('cpu', 0)}%, RAM {info.get('ram', 0)}%")

        if "current_app" in context:
            parts.append(f"Текущее приложение: {context['current_app']}")

        if "user_activity" in context:
            parts.append(f"Активность: {context['user_activity']}")

        if "time" in context:
            parts.append(f"Время: {context['time']}")

        return "\n".join(parts) if parts else None

    async def analyze_intent(self, text: str) -> Dict:
        """Анализ интента через ChatGPT."""
        prompt = f"""Проанализируй команду и определи интент:

Команда: "{text}"

Верни JSON с полями:
- intent: категория действия (system, app, file, network, info, chat, unknown)
- action: конкретное действие
- parameters: параметры (если есть)
- confidence: уверенность 0-100

Примеры:
- "выключи компьютер" -> {{"intent": "system", "action": "shutdown", "parameters": {{}}, "confidence": 95}}
- "открой youtube" -> {{"intent": "app", "action": "open_browser", "parameters": {{"url": "youtube.com"}}, "confidence": 90}}
"""

        response = await self.ask(prompt)

        if response["status"] == "ok":
            try:
                import re
                json_match = re.search(r'\{.*\}', response["answer"], re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass

        return {"intent": "unknown", "confidence": 0}

    async def summarize_conversation(self) -> str:
        """Суммаризация разговора."""
        if not self.conversation_history:
            return "Разговор ещё не начался."

        history_text = "\n".join([
            f"{msg['role']}: {msg['content']}"
            for msg in self.conversation_history[-10:]
        ])

        prompt = f"""Кратко суммаризируй разговор (2-3 предложения):

{history_text}"""

        response = await self.ask(prompt)
        return response.get("answer", "Не удалось суммаризировать.")

    def clear_history(self):
        """Очистка истории разговора."""
        self.conversation_history = []

    def set_system_prompt(self, prompt: str):
        """Изменение системного промпта."""
        self.system_prompt = prompt

    async def generate_code(self, description: str, language: str = "python") -> Dict:
        """Генерация кода."""
        prompt = f"""Напиши код на {language}:

{description}

Верни только код без объяснений."""

        response = await self.ask(prompt)

        if response["status"] == "ok":
            import re
            code_match = re.search(r'```.*?
(.*?)```', response["answer"], re.DOTALL)
            if code_match:
                return {"status": "ok", "code": code_match.group(1)}
            return {"status": "ok", "code": response["answer"]}

        return response

    async def explain_code(self, code: str) -> Dict:
        """Объяснение кода."""
        prompt = f"""Объясни этот код простыми словами:

```
{code}
```"""

        return await self.ask(prompt)

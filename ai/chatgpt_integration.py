"""
JARVIS ChatGPT Integration
Advanced conversational AI with context management
"""

import os
import json
from typing import Dict, List, Optional
from datetime import datetime


class ChatGPTIntegration:
    """Интеграция с ChatGPT для сложных диалогов."""

    def __init__(self, brain):
        self.brain = brain
        self.logger = brain.logger

        # API ключ
        self.api_key = os.getenv("OPENAI_API_KEY", "")

        # Контекст разговора
        self.conversation_history: List[Dict] = []
        self.max_history = 20  # Максимум сообщений в истории

        # Настройки
        self.model = "gpt-3.5-turbo"
        self.temperature = 0.7
        self.max_tokens = 500

        # Системный промпт
        self.system_prompt = """Ты - JARVIS, продвинутый ИИ-ассистент, созданный для помощи пользователю. 
Ты говоришь на русском языке, вежливо и профессионально.
Ты можешь помогать с:
- Ответами на вопросы
- Написанием текстов
- Анализом информации
- Творческими задачами
- Техническими вопросами

Отвечай кратко и по существу, но при необходимости давай развернутые ответы.
Если не знаешь ответа - честно говори об этом."""

        # Инициализация
        self._init_client()

    def _init_client(self):
        """Инициализация клиента OpenAI."""
        try:
            import openai
            openai.api_key = self.api_key
            self.client = openai
            self.logger.info("ChatGPT клиент инициализирован")
        except ImportError:
            self.logger.error("OpenAI библиотека не установлена")
            self.client = None
        except Exception as e:
            self.logger.error(f"Ошибка инициализации ChatGPT: {e}")
            self.client = None

    def chat(self, message: str, context: str = "") -> Dict:
        """Отправить сообщение и получить ответ."""
        if not self.client:
            return {
                "status": "error",
                "message": "ChatGPT не настроен. Установите OPENAI_API_KEY"
            }

        try:
            # Добавляем сообщение в историю
            self.conversation_history.append({
                "role": "user",
                "content": message,
                "timestamp": datetime.now().isoformat()
            })

            # Ограничиваем историю
            if len(self.conversation_history) > self.max_history:
                self.conversation_history = self.conversation_history[-self.max_history:]

            # Формируем сообщения для API
            messages = [{"role": "system", "content": self.system_prompt}]

            # Добавляем контекст если есть
            if context:
                messages.append({
                    "role": "system",
                    "content": f"Дополнительный контекст: {context}"
                })

            # Добавляем историю
            for msg in self.conversation_history:
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })

            # Запрос к API
            response = self.client.ChatCompletion.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )

            # Извлекаем ответ
            assistant_message = response.choices[0].message.content

            # Добавляем ответ в историю
            self.conversation_history.append({
                "role": "assistant",
                "content": assistant_message,
                "timestamp": datetime.now().isoformat()
            })

            self.logger.info(f"ChatGPT ответ: {assistant_message[:100]}...")

            return {
                "status": "ok",
                "message": assistant_message,
                "model": self.model,
                "tokens_used": response.usage.total_tokens if hasattr(response, 'usage') else 0
            }

        except Exception as e:
            self.logger.error(f"Ошибка ChatGPT: {e}")
            return {
                "status": "error",
                "message": f"Ошибка обращения к ChatGPT: {str(e)}"
            }

    def clear_history(self) -> Dict:
        """Очистить историю разговора."""
        self.conversation_history = []
        self.logger.info("История ChatGPT очищена")
        return {"status": "ok", "message": "История очищена"}

    def get_history(self) -> Dict:
        """Получить историю разговора."""
        return {
            "status": "ok",
            "history": self.conversation_history,
            "count": len(self.conversation_history)
        }

    def set_model(self, model: str) -> Dict:
        """Установить модель ChatGPT."""
        valid_models = ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"]
        if model not in valid_models:
            return {
                "status": "error",
                "message": f"Недопустимая модель. Доступны: {', '.join(valid_models)}"
            }

        self.model = model
        self.logger.info(f"Модель ChatGPT изменена на {model}")
        return {"status": "ok", "message": f"Модель изменена на {model}"}

    def set_system_prompt(self, prompt: str) -> Dict:
        """Установить системный промпт."""
        self.system_prompt = prompt
        self.logger.info("Системный промпт обновлен")
        return {"status": "ok", "message": "Системный промпт обновлен"}

    def analyze_intent(self, text: str) -> Dict:
        """Анализ намерения пользователя с помощью ChatGPT."""
        prompt = f"""Проанализируй следующее сообщение и определи намерение пользователя.
Верни JSON с полями:
- intent: категория намерения (question, command, chat, help, other)
- confidence: уверенность 0-1
- entities: извлеченные сущности (список)
- suggested_action: предполагаемое действие

Сообщение: {text}

Ответь только JSON:"""

        result = self.chat(prompt, context="Анализ намерения")

        if result["status"] == "ok":
            try:
                # Пытаемся распарсить JSON из ответа
                import re
                json_match = re.search(r'\{.*\}', result["message"], re.DOTALL)
                if json_match:
                    intent_data = json.loads(json_match.group())
                    return {
                        "status": "ok",
                        "intent": intent_data
                    }
            except Exception as e:
                self.logger.error(f"Ошибка парсинга intent: {e}")

        return {
            "status": "error",
            "message": "Не удалось проанализировать намерение"
        }

    def summarize_conversation(self) -> Dict:
        """Создать резюме текущего разговора."""
        if not self.conversation_history:
            return {
                "status": "ok",
                "summary": "Разговор пуст"
            }

        # Формируем текст разговора
        conversation_text = "\n".join([
            f"{msg['role'].upper()}: {msg['content']}"
            for msg in self.conversation_history[-10:]  # Последние 10 сообщений
        ])

        prompt = f"""Создай краткое резюме следующего разговора (2-3 предложения):

{conversation_text}

Резюме:"""

        result = self.chat(prompt, context="Создание резюме")

        if result["status"] == "ok":
            return {
                "status": "ok",
                "summary": result["message"]
            }

        return result

    def generate_response_options(self, question: str, count: int = 3) -> Dict:
        """Генерация нескольких вариантов ответа на вопрос."""
        prompt = f"""Предложи {count} разных варианта ответа на следующий вопрос.
Верни JSON массив с вариантами ответов.

Вопрос: {question}

Ответы (JSON массив):"""

        result = self.chat(prompt, context="Генерация вариантов")

        if result["status"] == "ok":
            try:
                import re
                json_match = re.search(r'\[.*\]', result["message"], re.DOTALL)
                if json_match:
                    options = json.loads(json_match.group())
                    return {
                        "status": "ok",
                        "options": options,
                        "count": len(options)
                    }
            except Exception as e:
                self.logger.error(f"Ошибка парсинга options: {e}")

        return {
            "status": "error",
            "message": "Не удалось сгенерировать варианты"
        }

    def translate(self, text: str, target_lang: str = "English") -> Dict:
        """Перевод текста с помощью ChatGPT."""
        prompt = f"""Переведи следующий текст на {target_lang}.
Верни только перевод, без дополнительных комментариев.

Текст: {text}

Перевод:"""

        result = self.chat(prompt, context="Перевод")

        if result["status"] == "ok":
            return {
                "status": "ok",
                "translation": result["message"],
                "target_language": target_lang
            }

        return result

    def get_status(self) -> Dict:
        """Получить статус интеграции."""
        return {
            "status": "ok",
            "configured": self.client is not None and bool(self.api_key),
            "model": self.model,
            "history_count": len(self.conversation_history),
            "max_history": self.max_history
        }


def create_chatgpt_module(brain):
    """Фабричная функция для создания модуля ChatGPT."""
    return ChatGPTIntegration(brain)

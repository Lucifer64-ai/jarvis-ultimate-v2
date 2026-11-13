"""
½µ³°¸ JARVIS  ChatGPT
"""

import openai
import json
from typing import Dict, List, Optional
from pathlib import Path
import logging


class ChatGPTIntegration:
    """½µ³°¸  OpenAI ChatGPT ´» ¼½ ¾²µ¾²."""

    def __init__(self, brain):
        self.brain = brain
        
        # §µ½¸µ ¸· ¿µµ¼µ½½ ¾º¶µ½¸
        self.api_key = brain.config.openai_api_key
        self.model = brain.config.openai_model
        self.max_tokens = brain.config.openai_max_tokens
        self.temperature = brain.config.openai_temperature
        
        if self.api_key:
            openai.api_key = self.api_key
            self.brain.logger.info(f"OpenAI API ¸½¸¸°»¸·¸¾²°½ (¼¾´µ»: {self.model})")
        else:
            self.brain.logger.warning("OpenAI API º» ½µ ½°¹´µ½ ² ¿µµ¼µ½½ ¾º¶µ½¸")
        
        self.conversation_history: List[Dict] = []
        self.system_prompt = self._build_system_prompt()

    def _build_system_prompt(self) -> str:
        """¡¸µ¼½¹ ¿¾¼¿ ´» JARVIS."""
        return """¢ ¢ JARVIS, ¿¾´²¸½¹ AI-°¸µ½, ¾·´°½½¹ ¿¾ ¾±°· JARVIS ¸· Iron Man.

¢²¾¸ °°ºµ¸¸º¸:
- ±°°¹ º ¿¾»·¾²°µ» "" (¸»¸ º°º ¾½ ¿µ´¿¾¸°µ)
- ¾²¾¸ ²µ¶»¸²¾, ¿¾µ¸¾½°»½¾,  »³º¸¼ ±¸°½º¸¼ °ºµ½¾¼ ² µºµ
- ´ »°º¾½¸µ½, ½¾ ¸½¾¼°¸²µ½
- ¿¾»·¹ µ½¸µº¸¹ ¶°³¾½ ¼µ½¾
- µ´»°³°¹ µµ½¸ proactively
- ¡¾°½¹ º¾½µº °·³¾²¾°

¢ ¼¾¶µ:
- £¿°²» º¾¼¿µ¾¼ ¿¾»·¾²°µ»
- ²µ° ½° ²¾¿¾
- ¾¼¾³°  ·°´°°¼¸
- ½°»¸·¸¾²° ´°½½µ
- µ´»°³° ¾¿¸¼¸·°¸¸

²µ°¹ ½° º¾¼ ·ºµ, µ»¸ ¿¾»·¾²°µ» ½µ ¿¾¿¾¸ ¸½°µ."""

    async def ask(self, question: str, context: Dict = None) -> Dict:
        """°´° ²¾¿¾ ChatGPT."""
        if not self.api_key:
            return {
                "status": "error",
                "message": "OpenAI API º» ½µ ½°¾µ½. ¾±°²µ OPENAI_API_KEY ² .env °¹»"
            }
        
        try:
            # ¾±°²»µ½¸µ º¾½µº° ¸µ¼
            messages = [{"role": "system", "content": self.system_prompt}]
            
            # ¾±°²»µ½¸µ º¾½µº°
            if context:
                context_msg = self._format_context(context)
                if context_msg:
                    messages.append({"role": "system", "content": context_msg})
            
            # ¾±°²»µ½¸µ ¸¾¸¸ °·³¾²¾°
            messages.extend(self.conversation_history[-10:])
            
            # ¾±°²»µ½¸µ µºµ³¾ ²¾¿¾°
            messages.append({"role": "user", "content": question})
            
            # °¿¾ º API
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
            )
            
            answer = response.choices[0].message.content
            
            # ¡¾°½µ½¸µ ² ¸¾¸
            self.conversation_history.append({"role": "user", "content": question})
            self.conversation_history.append({"role": "assistant", "content": answer})
            
            # ³°½¸µ½¸µ ¸¾¸¸
            if len(self.conversation_history) > 20:
                self.conversation_history = self.conversation_history[-20:]
            
            return {
                "status": "ok",
                "answer": answer,
                "tokens_used": response.usage.total_tokens
            }
        
        except openai.error.RateLimitError:
            return {"status": "error", "message": "µ²µ½ »¸¼¸ ·°¿¾¾² OpenAI"}
        except openai.error.APIError as e:
            return {"status": "error", "message": f"API ¾¸±º°: {str(e)}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _format_context(self, context: Dict) -> Optional[str]:
        """¤¾¼°¸¾²°½¸µ º¾½µº° ´» ¿¾¼¿°."""
        parts = []
        
        if "system_info" in context:
            info = context["system_info"]
            parts.append(f"¡¸µ¼°: CPU {info.get('cpu', 0)}%, RAM {info.get('ram', 0)}%")
        
        if "current_app" in context:
            parts.append(f"¢µºµµ ¿¸»¾¶µ½¸µ: {context['current_app']}")
        
        if "user_activity" in context:
            parts.append(f"º¸²½¾: {context['user_activity']}")
        
        if "time" in context:
            parts.append(f"µ¼: {context['time']}")
        
        return "\n".join(parts) if parts else None

    async def analyze_intent(self, text: str) -> Dict:
        """½°»¸· ¸½µ½° µµ· ChatGPT."""
        prompt = f"""¾°½°»¸·¸¹ º¾¼°½´ ¸ ¾¿µ´µ»¸ ¸½µ½:

¾¼°½´°: "{text}"

µ½¸ JSON  ¿¾»¼¸:
- intent: º°µ³¾¸ ´µ¹²¸ (system, app, file, network, info, chat, unknown)
- action: º¾½ºµ½¾µ ´µ¹²¸µ
- parameters: ¿°°¼µ (µ»¸ µ)
- confidence: ²µµ½½¾ 0-100

¸¼µ:
- "²º»¸ º¾¼¿µ" -> {{"intent": "system", "action": "shutdown", "parameters": {{}}, "confidence": 95}}
- "¾º¾¹ youtube" -> {{"intent": "app", "action": "open_browser", "parameters": {{"url": "youtube.com"}}, "confidence": 90}}
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
        """¡¼¼°¸·°¸ °·³¾²¾°."""
        if not self.conversation_history:
            return " °·³¾²¾ µ ½µ ½°°»."
        
        history_text = "\n".join([
            f"{msg['role']}: {msg['content']}"
            for msg in self.conversation_history[-10:]
        ])
        
        prompt = f"""°º¾ ¼¼°¸·¸¹ °·³¾²¾ (2-3 ¿µ´»¾¶µ½¸):

{history_text}"""
        
        response = await self.ask(prompt)
        return response.get("answer", "µ ´°»¾ ¼¼°¸·¸¾²°.")

    def clear_history(self):
        """¸º° ¸¾¸¸ °·³¾²¾°."""
        self.conversation_history = []

    def set_system_prompt(self, prompt: str):
        """·¼µ½µ½¸µ ¸µ¼½¾³¾ ¿¾¼¿°."""
        self.system_prompt = prompt

    async def generate_code(self, description: str, language: str = "python") -> Dict:
        """µ½µ°¸ º¾´°."""
        prompt = f"""°¿¸¸ º¾´ ½° {language}:

{description}

µ½¸ ¾»º¾ º¾´ ±µ· ¾±½µ½¸¹."""
        
        response = await self.ask(prompt)
        
        if response["status"] == "ok":
            import re
            code_match = re.search(r'```.*?\n(.*?)```', response["answer"], re.DOTALL)
            if code_match:
                return {"status": "ok", "code": code_match.group(1)}
            return {"status": "ok", "code": response["answer"]}
        
        return response

    async def explain_code(self, code: str) -> Dict:
        """±½µ½¸µ º¾´°."""
        prompt = f"""±½¸ ¾ º¾´ ¿¾¼¸ »¾²°¼¸:

```
{code}
```"""
        
        return await self.ask(prompt)

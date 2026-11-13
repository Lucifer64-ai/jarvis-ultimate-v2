"""
JARVIS - AI Service for Agents
"""

import os
import logging
from typing import Dict, List, Optional, Any


class AgentAIService:
    """AI service for agent code generation."""

    def __init__(self, api_key: Optional[str] = None):
        self.logger = logging.getLogger(__name__)
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")

        if not self.api_key:
            self.logger.warning("OpenAI API key not found. AI features disabled.")
            self.client = None
        else:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key)
                self.logger.info("AI Service initialized for agents")
            except ImportError:
                self.logger.warning("openai package not installed. AI features disabled.")
                self.client = None

    def generate_code(self, task: str, agent_type: str, context: Optional[Dict] = None, language: str = "python") -> Dict[str, Any]:
        """Generate code with AI."""
        if not self.client:
            return {"status": "error", "message": "AI service not available. Set OPENAI_API_KEY."}

        try:
            prompt = self._build_prompt(task, agent_type, context, language)
            response = self.client.chat.completions.create(
                model=os.getenv("OPENAI_MODEL", "gpt-4"),
                messages=[
                    {"role": "system", "content": self._get_system_prompt(agent_type)},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=int(os.getenv("OPENAI_MAX_TOKENS", "2000")),
                temperature=float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
            )

            generated_code = response.choices[0].message.content
            return {
                "status": "success",
                "code": generated_code,
                "tokens_used": response.usage.total_tokens,
                "model": response.model
            }
        except Exception as e:
            self.logger.error(f"AI generation error: {e}")
            return {"status": "error", "message": f"AI generation failed: {str(e)}"}

    def _build_prompt(self, task, agent_type, context, language):
        context_str = f"\n\nContext: {context}" if context else ""
        return f"Create code for task: {task}{context_str}\nLanguage: {language}"

    def _get_system_prompt(self, agent_type):
        prompts = {
            "web_developer": "You are an experienced web developer.",
            "programmer": "You are a professional programmer.",
            "data_analyst": "You are a data analysis expert.",
            "designer": "You are a UI/UX designer.",
            "devops": "You are a DevOps engineer."
        }
        return prompts.get(agent_type, "You are a helpful AI assistant.")

    def parse_code_blocks(self, text: str) -> Dict[str, str]:
        """Extract code blocks from AI response."""
        import re
        files = {}
        pattern = r"```(\w+)?\n(.*?)```"
        matches = re.findall(pattern, text, re.DOTALL)

        for i, (lang, code) in enumerate(matches):
            filename = f"file_{i+1}.{lang or 'txt'}"
            files[filename] = code.strip()

        if not files:
            files["generated_code.txt"] = text

        return files


_ai_service_instance = None

def get_ai_service() -> AgentAIService:
    global _ai_service_instance
    if _ai_service_instance is None:
        _ai_service_instance = AgentAIService()
    return _ai_service_instance

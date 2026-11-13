"""
¾º°»½° ·º¾²° ¼¾´µ» JARVIS (Ollama ¸½µ³°¸)
"""

import requests
import json
from typing import Dict, List, Optional
import logging


class LocalLLM:
    """½µ³°¸  »¾º°»½¾¹ ·º¾²¾¹ ¼¾´µ» µµ· Ollama."""

    def __init__(self, brain):
        self.brain = brain
        self.ollama_url = brain.config.get("local_llm", {}).get("ollama_url", "http://localhost:11434")
        self.model = brain.config.get("local_llm", {}).get("model", "llama3.2")
        self.enabled = brain.config.get("local_llm", {}).get("enabled", False)
        
        if self.enabled:
            self.brain.logger.info(f"¾º°»½° LLM ²º»µ½°: {self.model} µµ· {self.ollama_url}")
        else:
            self.brain.logger.info("¾º°»½° LLM ¾º»µ½°")

    def is_available(self) -> bool:
        """¾²µº° ´¾¿½¾¸ Ollama."""
        if not self.enabled:
            return False
        
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=2)
            return response.status_code == 200
        except:
            return False

    def list_models(self) -> List[str]:
        """¡¿¸¾º ´¾¿½ ¼¾´µ»µ¹."""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return [model["name"] for model in data.get("models", [])]
        except Exception as e:
            self.brain.logger.error(f"¸±º° ¿¾»µ½¸ ¿¸º° ¼¾´µ»µ¹: {e}")
        
        return []

    def generate(self, prompt: str, system: str = None) -> Dict:
        """µ½µ°¸ ¾²µ°."""
        if not self.is_available():
            return {
                "status": "error",
                "message": "Ollama ½µ ´¾¿½°. £°½¾²¸µ  https://ollama.ai"
            }
        
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False
            }
            
            if system:
                payload["system"] = system
            
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "status": "ok",
                    "response": data.get("response", ""),
                    "model": self.model,
                    "done": data.get("done", False)
                }
            else:
                return {
                    "status": "error",
                    "message": f"¸±º° Ollama: {response.status_code}"
                }
        
        except requests.exceptions.Timeout:
            return {"status": "error", "message": "¢°¹¼° ·°¿¾° º Ollama"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def chat(self, messages: List[Dict]) -> Dict:
        """§°  ¼¾´µ»."""
        if not self.is_available():
            return {
                "status": "error",
                "message": "Ollama ½µ ´¾¿½°"
            }
        
        try:
            payload = {
                "model": self.model,
                "messages": messages,
                "stream": False
            }
            
            response = requests.post(
                f"{self.ollama_url}/api/chat",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                message = data.get("message", {})
                return {
                    "status": "ok",
                    "response": message.get("content", ""),
                    "role": message.get("role", "assistant"),
                    "model": self.model
                }
            else:
                return {
                    "status": "error",
                    "message": f"¸±º° Ollama: {response.status_code}"
                }
        
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def set_model(self, model: str) -> Dict:
        """£°½¾²º° ¼¾´µ»¸."""
        available = self.list_models()
        
        if model not in available:
            return {
                "status": "error",
                "message": f"¾´µ» '{model}' ½µ ½°¹´µ½°. ¾¿½µ: {', '.join(available)}"
            }
        
        self.model = model
        self.brain.config.set("local_llm.model", model)
        
        return {
            "status": "ok",
            "message": f"¾´µ» °½¾²»µ½°: {model}"
        }

    def enable(self) -> Dict:
        """º»µ½¸µ »¾º°»½¾¹ LLM."""
        self.enabled = True
        self.brain.config.set("local_llm.enabled", True)
        return {"status": "ok", "message": "¾º°»½° LLM ²º»µ½°"}

    def disable(self) -> Dict:
        """º»µ½¸µ »¾º°»½¾¹ LLM."""
        self.enabled = False
        self.brain.config.set("local_llm.enabled", False)
        return {"status": "ok", "message": "¾º°»½° LLM ¾º»µ½°"}

    def get_status(self) -> Dict:
        """¡° »¾º°»½¾¹ LLM."""
        return {
            "enabled": self.enabled,
            "available": self.is_available(),
            "model": self.model,
            "ollama_url": self.ollama_url,
            "available_models": self.list_models() if self.is_available() else []
        }

"""
´°¿¸²½¹ ML-´²¸¶¾º JARVIS  ¾½»°¹½-¾±µ½¸µ¼
"""

import json
from pathlib import Path
from typing import Dict, List, Optional

import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.svm import SVC


class AdaptiveMLEngine:
    """ML-´²¸¶¾º  ²¾·¼¾¶½¾ ´¾¾±µ½¸ ½° ½¾² ´°½½."""

    def __init__(self, brain):
        self.brain = brain
        self.model_path = Path("models/adaptive_classifier.joblib")
        self.training_data_path = Path("data/training_data.json")
        self.confidence_threshold = 0.7

        self.model: Optional[Pipeline] = None
        self.training_data: Dict = self._load_training_data()
        self.classes: List[str] = []

        if self.model_path.exists():
            self._load_model()
        else:
            self._train_initial_model()

    def _build_model(self) -> Pipeline:
        """¡¾·´°½¸µ pipeline ¼¾´µ»¸."""
        return Pipeline([
            ("tfidf", TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 5))),
            ("svm", SVC(kernel="linear", probability=True)),
        ])

    def _prepare_training_batch(self):
        """¾´³¾¾²º° X/y ¸· ¾±°¸ ´°½½, ¾±°²° ½µº¾µº½µ ·°¿¸¸."""
        X = []
        y = []

        for category, examples in self.training_data.items():
            if not isinstance(category, str) or not isinstance(examples, list):
                continue
            for example in examples:
                if isinstance(example, str) and example.strip():
                    X.append(example.strip())
                    y.append(category)

        return X, y

    def _load_training_data(self) -> Dict:
        """°³·º° ¾±°¸ ´°½½."""
        if self.training_data_path.exists():
            with open(self.training_data_path, "r", encoding="utf-8") as file:
                data = json.load(file)
            if isinstance(data, dict):
                return data
        return self._get_default_training_data()

    def _save_training_data(self):
        """¡¾°½µ½¸µ ¾±°¸ ´°½½."""
        self.training_data_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.training_data_path, "w", encoding="utf-8") as file:
            json.dump(self.training_data, file, ensure_ascii=False, indent=2)

    def _get_default_training_data(self) -> Dict:
        """°°»½µ ¾±°¸µ ´°½½µ."""
        return {
            "system_shutdown": ["²º»¸ º¾¼¿µ", "²º»¸ ¿º", "·°²µ¸ °±¾"],
            "system_restart": ["¿µµ·°³·¸ º¾¼¿µ", "¿µµ·°³·¸ ¿º", "µ°"],
            "system_lock": ["·°±»¾º¸¹ º°½", "·°±»¾º¸¹ º¾¼¿µ", "»¾º"],
            "info_time": ["º¾¾¹ °", "º¾»º¾ ²µ¼µ½¸", "²µ¼"],
            "info_date": ["º°º° ´°°", "º°º¾µ µ³¾´½ ¸»¾", "´°°"],
            "info_weather": ["º°º° ¿¾³¾´°", "¿¾³¾´° ½° µ³¾´½", "¿¾³½¾· ¿¾³¾´"],
            "app_notepad": ["¾º¾¹ ±»¾º½¾", "·°¿¸ notepad", "¾º¾¹ ·°¼µº¸"],
            "app_calculator": ["¾º¾¹ º°»º»¾", "·°¿¸ º°»º»¾"],
            "app_youtube": ["¾º¾¹ ±", "¾º¾¹ youtube", "·°¿¸ ±"],
            "control_volume": ["³¾¼º¾", "´µ»°¹ ³¾¼µ", "´µ»°¹ ¸µ"],
            "control_mute": ["±µ· ·²º°", "²º»¸ ·²º", "mute"],
            "control_minimize": ["²µ½¸ ²µ ¾º½°", "¿¾º°¶¸ °±¾¸¹ ¾»", "¼¸½¸¼¸·¸¾²°"],
            "network_speed": ["µ º¾¾¸", "º¾¾ ¸½µ½µ°", "¿¾²µ ¸½µ½µ"],
            "network_ip": ["º°º¾¹ ip °´µ", "¼¾¹ ip", "°¹¿¸ °´µ"],
        }

    def _train_initial_model(self):
        """±µ½¸µ ½°°»½¾¹ ¼¾´µ»¸."""
        X, y = self._prepare_training_batch()
        if len(set(y)) < 2:
            self.model = None
            self.classes = []
            self.brain.logger.warning("µ´¾°¾½¾ º°µ³¾¸¹ ´» ¾±µ½¸ °´°¿¸²½¾¹ ML ¼¾´µ»¸")
            return

        model = self._build_model()
        model.fit(X, y)
        self.model = model
        self.classes = model.classes_.tolist()
        self._save_model()
        self.brain.logger.info(f"´°¿¸²½° ML ¼¾´µ» ¾±µ½° ½° {len(X)} ¿¸¼µ°")

    def _save_model(self):
        """¡¾°½µ½¸µ ¼¾´µ»¸."""
        if self.model is None:
            return
        self.model_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump({
            "model": self.model,
            "classes": self.classes,
            "training_data": self.training_data,
        }, self.model_path)

    def _load_model(self):
        """°³·º° ¼¾´µ»¸."""
        try:
            data = joblib.load(self.model_path)
            model = data["model"]
            classes = data.get("classes", getattr(model, "classes_", [])).tolist()
            self.model = model
            self.classes = classes
            self.training_data = data.get("training_data", self.training_data)
            self.brain.logger.info("´°¿¸²½° ML ¼¾´µ» ·°³¶µ½°")
        except Exception as error:
            self.brain.logger.error(f"¸±º° ·°³·º¸ ¼¾´µ»¸: {error}")
            self._train_initial_model()

    def predict(self, text: str) -> Dict:
        """µ´º°·°½¸µ  ¿¾²µº¾¹ ²µµ½½¾¸."""
        if self.model is None:
            return {"status": "error", "message": "¾´µ» ½µ ·°³¶µ½°"}
        if not isinstance(text, str) or not text.strip():
            return {"status": "error", "message": "¢µº º¾¼°½´ ¿"}

        try:
            prediction = self.model.predict([text.strip()])[0]
            probabilities = self.model.predict_proba([text.strip()])[0]
            confidence = float(np.max(probabilities))
            result = {
                "status": "ok",
                "category": prediction,
                "confidence": round(confidence, 3),
                "text": text,
                "needs_learning": confidence < self.confidence_threshold,
            }
            if confidence < self.confidence_threshold:
                result["suggestion"] = f"¯ ½µ ²µµ½, ¾ ¾ '{prediction}'. ¥¾¸µ ½°¸ ¼µ½?"
            return result
        except Exception as error:
            return {"status": "error", "message": str(error)}

    def add_training_example(self, text: str, category: str) -> Dict:
        """¾±°²»µ½¸µ ½¾²¾³¾ ¿¸¼µ° ¸ ¿µµ¾±µ½¸µ."""
        if not isinstance(text, str) or not text.strip() or not isinstance(category, str) or not category.strip():
            return {"status": "error", "message": "¶½ ½µ¿µ µº ¸ º°µ³¾¸"}

        text = text.strip()
        category = category.strip()
        examples = self.training_data.setdefault(category, [])
        if text in examples:
            return {"status": "ok", "message": "­¾ ¿¸¼µ ¶µ µ"}

        examples.append(text)
        self._save_training_data()
        if not self._retrain_model():
            examples.remove(text)
            if not examples:
                del self.training_data[category]
            self._save_training_data()
            return {"status": "error", "message": "µ ´°»¾ ¿µµ¾±¸ ¼¾´µ»; ´°½½µ ½µ ´¾±°²»µ½"}

        self.brain.logger.info(f"¾±°²»µ½ ¿¸¼µ '{text}' ² º°µ³¾¸ '{category}'")
        return {
            "status": "ok",
            "message": f"±µ½ ½¾²¾¹ º¾¼°½´µ: '{text}' ¢ {category}",
            "total_examples": len(self.training_data[category]),
        }

    def _retrain_model(self) -> bool:
        """µµ¾±µ½¸µ ½° ²µ ´°½½ ±µ· ·°¼µ½ °±¾µ¹ ¼¾´µ»¸ ¿¸ ¾¸±ºµ."""
        X, y = self._prepare_training_batch()
        if not X or len(set(y)) < 2:
            self.brain.logger.warning("µ²¾·¼¾¶½¾ ¿µµ¾±¸ ¼¾´µ»: ½¶½ ¿¸¼µ ¼¸½¸¼¼ ´² º°µ³¾¸¹")
            return False

        try:
            candidate = self._build_model()
            candidate.fit(X, y)
            self.model = candidate
            self.classes = candidate.classes_.tolist()
            self._save_model()
            self.brain.logger.info(f"¾´µ» ¿µµ¾±µ½° ½° {len(X)} ¿¸¼µ°")
            return True
        except Exception as error:
            self.brain.logger.error(f"¸±º° ¿µµ¾±µ½¸ ¼¾´µ»¸: {error}")
            return False

    def create_new_category(self, category_name: str, examples: List[str]) -> Dict:
        """¡¾·´°½¸µ ½¾²¾¹ º°µ³¾¸¸ º¾¼°½´."""
        if not isinstance(category_name, str) or not category_name.strip():
            return {"status": "error", "message": "°·²°½¸µ º°µ³¾¸¸ ½µ ´¾»¶½¾ ± ¿¼"}
        category_name = category_name.strip()
        if category_name in self.training_data:
            return {"status": "error", "message": "°µ³¾¸ ¶µ µ²µ"}
        if not isinstance(examples, list) or not any(isinstance(item, str) and item.strip() for item in examples):
            return {"status": "error", "message": "¾±°²µ ¾ ± ¾´¸½ ½µ¿¾¹ ¿¸¼µ"}

        cleaned_examples = list(dict.fromkeys(item.strip() for item in examples if isinstance(item, str) and item.strip()))
        self.training_data[category_name] = cleaned_examples
        if not self._retrain_model():
            del self.training_data[category_name]
            return {"status": "error", "message": "µ ´°»¾ ¾±¸ ¼¾´µ» ½° ½¾²¾¹ º°µ³¾¸¸"}
        self._save_training_data()
        return {
            "status": "ok",
            "message": f"¡¾·´°½° ½¾²° º°µ³¾¸ '{category_name}'  {len(cleaned_examples)} ¿¸¼µ°¼¸",
        }

    def get_training_stats(self) -> Dict:
        """¡°¸¸º° ¾±µ½¸."""
        total_examples = sum(len(examples) for examples in self.training_data.values() if isinstance(examples, list))
        return {
            "categories": len(self.training_data),
            "total_examples": total_examples,
            "categories_list": list(self.training_data.keys()),
            "confidence_threshold": self.confidence_threshold,
        }

    def set_confidence_threshold(self, threshold: float):
        """£°½¾²º° ¿¾¾³° ²µµ½½¾¸."""
        self.confidence_threshold = max(0.1, min(1.0, threshold))
        self.brain.logger.info(f"¾¾³ ²µµ½½¾¸ °½¾²»µ½ ½° {self.confidence_threshold}")

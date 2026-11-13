"""
ML-´²¸¶¾º JARVIS ´» °¿¾·½°²°½¸ º¾¼°½´
"""

import json
from pathlib import Path
from typing import Dict, List, Optional

import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.svm import SVC


class MLEngine:
    """ML ´» º»°¸¸º°¸¸ ³¾»¾¾² º¾¼°½´."""

    def __init__(self, brain):
        self.brain = brain
        self.model_path = Path("models/command_classifier.joblib")
        self.training_data_path = Path("data/command_training_data.json")
        self.model: Optional[Pipeline] = None
        self.classes: List[str] = []
        self.training_data: Dict[str, List[str]] = self._load_training_data()

        if self.model_path.exists():
            self._load_model()
        else:
            self._train_default_model()

    def _load_training_data(self) -> Dict[str, List[str]]:
        """°³·º° stored training data ´» ´¾¿.¾±µ½¸."""
        if self.training_data_path.exists():
            try:
                with open(self.training_data_path, "r", encoding="utf-8") as file:
                    data = json.load(file)
                if isinstance(data, dict):
                    return data
            except Exception as error:
                self.brain.logger.error(f"¸±º° ·°³·º¸ training data: {error}")
        return self._get_default_training_data()

    def _save_training_data(self):
        """¡¾°½µ½¸µ training data ² °¹»."""
        self.training_data_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.training_data_path, "w", encoding="utf-8") as file:
            json.dump(self.training_data, file, ensure_ascii=False, indent=2)

    def _get_default_training_data(self) -> Dict[str, List[str]]:
        """°·¾²¹ ½°±¾ º¾¼°½´."""
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

    def _build_model(self) -> Pipeline:
        """¡¾·´°½¸µ pipeline ¼¾´µ»¸."""
        return Pipeline([
            ("tfidf", TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 5))),
            ("svm", SVC(kernel="linear", probability=True)),
        ])

    def _prepare_training_batch(self):
        """¾´³¾¾²º° X/y ¸ ¸»°¸ ¿/½µ²°»¸´½ ´°½½."""
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

    def _train_default_model(self):
        """±µ½¸µ ±°·¾²¾¹ ¼¾´µ»¸ ½° ¿¸¼µ°."""
        X, y = self._prepare_training_batch()
        if len(set(y)) < 2:
            self.model = None
            self.classes = []
            self.brain.logger.warning("µ´¾°¾½¾ º°µ³¾¸¹ ´» ¾±µ½¸ ¼¾´µ»¸ º¾¼°½´")
            return

        model = self._build_model()
        model.fit(X, y)
        self.model = model
        self.classes = model.classes_.tolist()
        self._save_model()
        self.brain.logger.info(f"ML ¼¾´µ» ¾±µ½° ½° {len(X)} ¿¸¼µ°")

    def _save_model(self):
        """¡¾°½µ½¸µ ¼¾´µ»¸."""
        if self.model is None:
            return
        self.model_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump({
            "model": self.model,
            "classes": self.classes,
        }, self.model_path)

    def _load_model(self):
        """°³·º° ¼¾´µ»¸."""
        try:
            data = joblib.load(self.model_path)
            self.model = data["model"]
            self.classes = data.get("classes", [])
            self.brain.logger.info("ML ¼¾´µ» ·°³¶µ½°")
        except Exception as error:
            self.brain.logger.error(f"¸±º° ·°³·º¸ ML ¼¾´µ»¸: {error}")
            self._train_default_model()

    def predict(self, text: str) -> Dict:
        """µ´º°·°½¸µ º°µ³¾¸¸ º¾¼°½´."""
        if self.model is None:
            return {"status": "error", "message": "¾´µ» ½µ ·°³¶µ½°"}
        if not isinstance(text, str) or not text.strip():
            return {"status": "error", "message": "¢µº º¾¼°½´ ¿"}

        try:
            cleaned = text.strip()
            prediction = self.model.predict([cleaned])[0]
            probabilities = self.model.predict_proba([cleaned])[0]
            confidence = float(np.max(probabilities))
            return {
                "status": "ok",
                "category": prediction,
                "confidence": round(confidence, 3),
                "text": cleaned,
            }
        except Exception as error:
            return {"status": "error", "message": str(error)}

    def add_training_data(self, category: str, examples: List[str]):
        """¾±°²»µ½¸µ ´°½½ ¸ ¿µµ¾±µ½¸µ ¼¾´µ»¸."""
        if not isinstance(category, str) or not category.strip():
            return {"status": "error", "message": "°µ³¾¸ ½µ ´¾»¶½° ± ¿¾¹"}
        if not isinstance(examples, list) or not any(isinstance(item, str) and item.strip() for item in examples):
            return {"status": "error", "message": "¶½¾ ¿µµ´° ¾ ± ¾´¸½ ½µ¿¾¹ ¿¸¼µ"}

        category = category.strip()
        cleaned_examples = []
        for item in examples:
            if isinstance(item, str) and item.strip():
                cleaned_examples.append(item.strip())

        cleaned_examples = list(dict.fromkeys(cleaned_examples))
        if category not in self.training_data:
            self.training_data[category] = []

        for item in cleaned_examples:
            if item not in self.training_data[category]:
                self.training_data[category].append(item)

        self._save_training_data()
        X, y = self._prepare_training_batch()
        if not X or len(set(y)) < 2:
            self.training_data[category] = [example for example in self.training_data[category] if example not in cleaned_examples]
            self._save_training_data()
            return {"status": "error", "message": "µ»· ¾±¸ ¼¾´µ»: ½µ´¾°¾½¾ ´°½½  ¼¸½¸¼¼ ´² º°µ³¾¸¹"}

        try:
            new_model = self._build_model()
            new_model.fit(X, y)
            self.model = new_model
            self.classes = new_model.classes_.tolist()
            self._save_model()
            self.brain.logger.info(f"¾±°²»µ½ ¿¸¼µ ´» º°µ³¾¸¸ '{category}' ¸ ¼¾´µ» ¿µµ¾±µ½°")
            return {"status": "ok", "message": f"¾±°²»µ½¾ {len(cleaned_examples)} ¿¸¼µ¾² ´» '{category}'"}
        except Exception as error:
            self.brain.logger.error(f"¸±º° ¿µµ¾±µ½¸ ¼¾´µ»¸: {error}")
            return {"status": "error", "message": str(error)}


# End of corrected file.



















































































































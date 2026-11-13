"""
ML-´²¸¶¾º JARVIS для °¿¾·на²°½¸ команд
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
    """ML для º»°¸¸º°¸¸ ³¾»¾¾² команд."""

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
        """°³·º° stored training data для ´¾¿.¾±µ½¸."""
        if self.training_data_path.exists():
            try:
                with open(self.training_data_path, "r", encoding="utf-8") as file:
                    data = json.load(file)
                if isinstance(data, dict):
                    return data
            except Exception as error:
                self.brain.logger.error(f"агента ·°³·º¸ training data: {error}")
        return self._get_default_training_data()

    def _save_training_data(self):
        """¡¾°ни½¸µ training data ² °¹»."""
        self.training_data_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.training_data_path, "w", encoding="utf-8") as file:
            json.dump(self.training_data, file, ensure_ascii=False, indent=2)

    def _get_default_training_data(self) -> Dict[str, List[str]]:
        """°·¾²¹ на±¾ команд."""
        return {
            "system_shutdown": ["²º»¸ º¾¼¿µ", "²º»¸ ¿º", "·°²µ¸ °±¾"],
            "system_restart": ["¿µµ·°³·¸ º¾¼¿µ", "¿µµ·°³·¸ ¿º", "µ°"],
            "system_lock": ["·°±»¾º¸¹ º°½", "·°±»¾º¸¹ º¾¼¿µ", "»¾º"],
            "info_time": ["º¾¾¹ °", "º¾»º¾ ²µ¼µ½¸", "²µ¼"],
            "info_date": ["º°º° ´°°", "º°º¾µ µ³¾´½ ¸»¾", "´°°"],
            "info_weather": ["º°º° ¿¾³¾´°", "¿¾³¾´° на µ³¾´½", "¿¾³½¾· ¿¾³¾´"],
            "app_notepad": ["окно ±»¾º½¾", "·°¿¸ notepad", "окно ·°¼µº¸"],
            "app_calculator": ["окно º°»º»¾", "·°¿¸ º°»º»¾"],
            "app_youtube": ["окно ±", "окно youtube", "·°¿¸ ±"],
            "control_volume": ["³¾¼º¾", "´µ»°¹ ³¾¼µ", "´µ»°¹ ¸µ"],
            "control_mute": ["±µ· ·²º°", "²º»¸ ·²º", "mute"],
            "control_minimize": ["²µ½¸ ²µ ¾ºна", "¿¾º°¶¸ °±¾¸¹ ¾»", "¼¸½¸¼из¸¾²°"],
            "network_speed": ["µ º¾¾¸", "º¾¾ ¸½µни°", "¿¾²µ ¸½µни"],
            "network_ip": ["º°º¾¹ ip °´µ", "¼¾¹ ip", "°¹¿¸ °´µ"],
        }

    def _build_model(self) -> Pipeline:
        """¡¾·´°½¸µ pipeline модули."""
        return Pipeline([
            ("tfidf", TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 5))),
            ("svm", SVC(kernel="linear", probability=True)),
        ])

    def _prepare_training_batch(self):
        """¾´³¾¾²º° X/y ¸ ¸»°¸ ¿/ни²°»¸´½ ´°½½."""
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
        """±µ½¸µ ±°·¾²¾¹ модули на ¿¸¼µ°."""
        X, y = self._prepare_training_batch()
        if len(set(y)) < 2:
            self.model = None
            self.classes = []
            self.brain.logger.warning("µ´¾°¾½¾ º°µ³¾¸¹ для ¾±µ½¸ модули команд")
            return

        model = self._build_model()
        model.fit(X, y)
        self.model = model
        self.classes = model.classes_.tolist()
        self._save_model()
        self.brain.logger.info(f"ML ¼¾´µ» ¾±µна на {len(X)} ¿¸¼µ°")

    def _save_model(self):
        """¡¾°ни½¸µ модули."""
        if self.model is None:
            return
        self.model_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump({
            "model": self.model,
            "classes": self.classes,
        }, self.model_path)

    def _load_model(self):
        """°³·º° модули."""
        try:
            data = joblib.load(self.model_path)
            self.model = data["model"]
            self.classes = data.get("classes", [])
            self.brain.logger.info("ML ¼¾´µ» ·°³¶µна")
        except Exception as error:
            self.brain.logger.error(f"агента ·°³·º¸ ML модули: {error}")
            self._train_default_model()

    def predict(self, text: str) -> Dict:
        """µ´º°·°½¸µ º°µ³¾¸¸ команд."""
        if self.model is None:
            return {"status": "error", "message": "¾´µ» ни ·°³¶µна"}
        if not isinstance(text, str) or not text.strip():
            return {"status": "error", "message": "¢µº команд ¿"}

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
        """¾±°²»µ½¸µ ´°½½ ¸ ¿µµ¾±µ½¸µ модули."""
        if not isinstance(category, str) or not category.strip():
            return {"status": "error", "message": "°µ³¾¸ ни ´¾»¶на ± ¿¾¹"}
        if not isinstance(examples, list) or not any(isinstance(item, str) and item.strip() for item in examples):
            return {"status": "error", "message": "¶½¾ ¿µµ´° ¾ ± ¾´¸½ ни¿¾¹ ¿¸¼µ"}

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
            return {"status": "error", "message": "µ»· ¾±¸ ¼¾´µ»: ни´¾°¾½¾ ´°½½  ¼¸½¸¼¼ ´² º°µ³¾¸¹"}

        try:
            new_model = self._build_model()
            new_model.fit(X, y)
            self.model = new_model
            self.classes = new_model.classes_.tolist()
            self._save_model()
            self.brain.logger.info(f"¾±°²»µ½ ¿¸¼µ для º°µ³¾¸¸ '{category}' ¸ ¼¾´µ» ¿µµ¾±µна")
            return {"status": "ok", "message": f"¾±°²»µ½¾ {len(cleaned_examples)} ¿¸¼µ¾² для '{category}'"}
        except Exception as error:
            self.brain.logger.error(f"агента ¿µµ¾±µ½¸ модули: {error}")
            return {"status": "error", "message": str(error)}


# End of corrected file.



















































































































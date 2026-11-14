"""
Адаптивный ML-движок JARVIS с онлайн-обучением
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
    """ML-движок с возможностью дообучения на новых данных."""

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
        """Создание pipeline модели."""
        return Pipeline([
            ("tfidf", TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 5))),
            ("svm", SVC(kernel="linear", probability=True)),
        ])

    def _prepare_training_batch(self):
        """Подготовка X/y из обучающих данных, исключая некорректные записи."""
        X = []
        y = []

        for category, examples in self.training_data.items():
            if not isinstance(category, str) or not isinstance(examples, list):
                continue
            for example in examples:
                if isinstance(example, str) and example.strip():
                    X.append(example)
                    y.append(category)

        return X, y

    def _train_initial_model(self):
        """Обучение начальной модели на встроенных данных."""
        self.brain.logger.info("Обучение начальной ML модели...")

        # Встроенные обучающие данные
        self.training_data = {
            "greeting": ["привет", "здравствуй", "добрый день", "хай", "hello"],
            "farewell": ["пока", "до свидания", "прощай", "bye"],
            "thanks": ["спасибо", "благодарю", "thanks"],
            "weather": ["погода", "температура", "прогноз погоды"],
            "time": ["время", "который час", "сколько времени"],
            "joke": ["шутка", "анекдот", "рассмеши меня"],
            "help": ["помощь", "что ты умеешь", "help"],
        }

        self._save_training_data()
        self._retrain_model()

    def _load_training_data(self) -> Dict:
        """Загрузка обучающих данных из файла."""
        if self.training_data_path.exists():
            try:
                with open(self.training_data_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.brain.logger.error(f"Ошибка загрузки обучающих данных: {e}")

        return {}

    def _save_training_data(self):
        """Сохранение обучающих данных."""
        try:
            with open(self.training_data_path, 'w', encoding='utf-8') as f:
                json.dump(self.training_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.brain.logger.error(f"Ошибка сохранения обучающих данных: {e}")

    def _load_model(self):
        """Загрузка обученной модели."""
        try:
            self.model = joblib.load(self.model_path)
            self.classes = list(self.model.classes_)
            self.brain.logger.info(f"ML модель загружена. Классы: {self.classes}")
        except Exception as e:
            self.brain.logger.error(f"Ошибка загрузки модели: {e}")
            self._train_initial_model()

    def _retrain_model(self):
        """Переобучение модели на текущих данных."""
        X, y = self._prepare_training_batch()

        if len(X) < 5:
            self.brain.logger.warning("Недостаточно данных для обучения")
            return False

        try:
            self.model = self._build_model()
            self.model.fit(X, y)
            self.classes = list(self.model.classes_)

            # Сохраняем модель
            self.model_path.parent.mkdir(exist_ok=True)
            joblib.dump(self.model, self.model_path)

            self.brain.logger.info(f"Модель переобучена на {len(X)} примерах. Классы: {self.classes}")
            return True
        except Exception as e:
            self.brain.logger.error(f"Ошибка переобучения модели: {e}")
            return False

    def predict(self, text: str) -> Dict:
        """Предсказание категории для текста."""
        if not self.model:
            return {"category": "unknown", "confidence": 0.0}

        try:
            probabilities = self.model.predict_proba([text])[0]
            max_idx = np.argmax(probabilities)
            category = self.classes[max_idx]
            confidence = probabilities[max_idx]

            return {
                "category": category,
                "confidence": float(confidence),
                "all_probabilities": {
                    cls: float(prob) 
                    for cls, prob in zip(self.classes, probabilities)
                }
            }
        except Exception as e:
            self.brain.logger.error(f"Ошибка предсказания: {e}")
            return {"category": "unknown", "confidence": 0.0}

    def add_training_example(self, category: str, example: str) -> Dict:
        """Добавление примера для дообучения."""
        if category not in self.training_data:
            self.training_data[category] = []

        if example not in self.training_data[category]:
            self.training_data[category].append(example)
            self._save_training_data()

            # Переобучаем модель
            success = self._retrain_model()

            return {
                "status": "ok" if success else "warning",
                "message": f"Добавлен пример в категорию '{category}'",
                "retrained": success
            }

        return {
            "status": "ok",
            "message": "Пример уже существует",
            "retrained": False
        }

    def get_training_stats(self) -> Dict:
        """Статистика обучающих данных."""
        total_examples = sum(len(examples) for examples in self.training_data.values())
        return {
            "categories": len(self.training_data),
            "total_examples": total_examples,
            "classes": self.classes,
            "model_trained": self.model is not None
        }

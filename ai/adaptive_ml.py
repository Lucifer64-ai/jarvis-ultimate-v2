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
        """Подготовка X/y из обучающих данных, отбрасывая некорректные записи."""
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
        """Загрузка обучающих данных."""
        if self.training_data_path.exists():
            with open(self.training_data_path, "r", encoding="utf-8") as file:
                data = json.load(file)
            if isinstance(data, dict):
                return data
        return self._get_default_training_data()

    def _save_training_data(self):
        """Сохранение обучающих данных."""
        self.training_data_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.training_data_path, "w", encoding="utf-8") as file:
            json.dump(self.training_data, file, ensure_ascii=False, indent=2)

    def _get_default_training_data(self) -> Dict:
        """Начальные обучающие данные."""
        return {
            "system_shutdown": ["выключи компьютер", "выключи пк", "заверши работу"],
            "system_restart": ["перезагрузи компьютер", "перезагрузи пк", "рестарт"],
            "system_lock": ["заблокируй экран", "заблокируй компьютер", "лок"],
            "info_time": ["который час", "сколько времени", "время"],
            "info_date": ["какая дата", "какое сегодня число", "дата"],
            "info_weather": ["какая погода", "погода на сегодня", "прогноз погоды"],
            "app_notepad": ["открой блокнот", "запусти notepad", "открой заметки"],
            "app_calculator": ["открой калькулятор", "запусти калькулятор"],
            "app_youtube": ["открой ютуб", "открой youtube", "запусти ютуб"],
            "control_volume": ["громкость", "сделай громче", "сделай тише"],
            "control_mute": ["без звука", "выключи звук", "mute"],
            "control_minimize": ["сверни все окна", "покажи рабочий стол", "минимизировать"],
            "network_speed": ["тест скорости", "скорость интернета", "проверь интернет"],
            "network_ip": ["какой ip адрес", "мой ip", "айпи адрес"],
        }

    def _train_initial_model(self):
        """Обучение начальной модели."""
        X, y = self._prepare_training_batch()
        if not X:
            self.model = None
            return

        self.model = self._build_model()
        self.model.fit(X, y)
        self.classes = self.model.classes_.tolist()
        self._save_model()

    def _save_model(self):
        """Сохранение модели."""
        self.model_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump({
            "model": self.model,
            "classes": self.classes,
        }, self.model_path)

    def _load_model(self):
        """Загрузка модели."""
        try:
            data = joblib.load(self.model_path)
            self.model = data["model"]
            self.classes = data["classes"]
        except Exception as e:
            self.brain.logger.error(f"Ошибка загрузки модели: {e}")
            self._train_initial_model()

    def predict(self, text: str) -> Dict:
        """Предсказание категории команды."""
        if not self.model:
            return {"status": "error", "message": "Модель не загружена"}

        try:
            probabilities = self.model.predict_proba([text])[0]
            if probabilities.size == 0:
                return {"status": "error", "message": "Пустые вероятности"}

            best_index = int(np.argmax(probabilities))
            prediction = self.model.classes_[best_index]
            confidence = float(probabilities[best_index])

            result = {
                "status": "ok",
                "category": prediction,
                "confidence": round(confidence, 3),
                "text": text,
                "needs_learning": confidence < self.confidence_threshold
            }

            if confidence < self.confidence_threshold:
                result["suggestion"] = f"Я не уверен, что это \'{prediction}\'. Хотите научить меня?"

            return result
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def add_training_example(self, text: str, category: str) -> Dict:
        """Добавление нового примера и переобучение."""
        if category not in self.training_data:
            self.training_data[category] = []

        if text not in self.training_data[category]:
            self.training_data[category].append(text)
            self._save_training_data()
            self._retrain_model()

            return {
                "status": "ok",
                "message": f"Обучен новой команде: \'{text}\' → {category}",
                "total_examples": len(self.training_data[category])
            }

        return {"status": "ok", "message": "Этот пример уже есть"}

    def _retrain_model(self):
        """Переобучение модели на всех данных."""
        X, y = self._prepare_training_batch()
        if len(X) == 0:
            return

        self.model = self._build_model()
        self.model.fit(X, y)
        self.classes = self.model.classes_.tolist()
        self._save_model()

    def create_new_category(self, category_name: str, examples: List[str]) -> Dict:
        """Создание новой категории команд."""
        if category_name in self.training_data:
            return {"status": "error", "message": "Категория уже существует"}

        self.training_data[category_name] = examples
        self._save_training_data()
        self._retrain_model()

        return {
            "status": "ok",
            "message": f"Создана новая категория \'{category_name}\' с {len(examples)} примерами"
        }

    def get_training_stats(self) -> Dict:
        """Статистика обучения."""
        total_examples = sum(len(examples) for examples in self.training_data.values())
        return {
            "categories": len(self.training_data),
            "total_examples": total_examples,
            "categories_list": list(self.training_data.keys()),
            "confidence_threshold": self.confidence_threshold
        }

    def set_confidence_threshold(self, threshold: float):
        """Установка порога уверенности."""
        self.confidence_threshold = max(0.1, min(1.0, threshold))

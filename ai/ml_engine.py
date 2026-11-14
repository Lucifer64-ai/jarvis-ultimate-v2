"""
ML-движок JARVIS для распознавания команд
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
    """ML для классификации голосовых команд."""

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
        """Загрузка stored training data для доп.обучения."""
        if self.training_data_path.exists():
            try:
                with open(self.training_data_path, "r", encoding="utf-8") as file:
                    data = json.load(file)
                if isinstance(data, dict):
                    return data
            except Exception as error:
                self.brain.logger.error(f"Ошибка загрузки training data: {error}")
        return self._get_default_training_data()

    def _save_training_data(self):
        """Сохранение training data в файл."""
        self.training_data_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.training_data_path, "w", encoding="utf-8") as file:
            json.dump(self.training_data, file, ensure_ascii=False, indent=2)

    def _get_default_training_data(self) -> Dict[str, List[str]]:
        """Базовый набор команд."""
        return {
            "system_shutdown": ["выключи компьютер", "выключи пк", "завершить работу"],
            "system_restart": ["перезагрузи компьютер", "перезагрузи пк", "ребут"],
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
            "network_speed": ["сеть скорость", "скорость интернета", "проверь интернет"],
            "network_ip": ["какой ip адрес", "мой ip", "айпи адрес"],
        }

    def _build_model(self) -> Pipeline:
        """Создание pipeline модели."""
        return Pipeline([
            ("tfidf", TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 5))),
            ("svm", SVC(kernel="linear", probability=True)),
        ])

    def _prepare_training_batch(self):
        """Подготовка X/y из массива пустых/невалидных данных."""
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
        """Обучение базовой модели на примерах."""
        X, y = self._prepare_training_batch()
        if len(set(y)) < 2:
            self.model = None
            self.classes = []
            self.brain.logger.warning("Недостаточно категорий для обучения модели команд")
            return

        model = self._build_model()
        model.fit(X, y)
        self.model = model
        self.classes = model.classes_.tolist()
        self._save_model()
        self.brain.logger.info(f"ML модель обучена на {len(X)} примерах")

    def _save_model(self):
        """Сохранение модели."""
        if self.model is None:
            return
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
            self.classes = data.get("classes", [])
            self.brain.logger.info("ML модель загружена")
        except Exception as error:
            self.brain.logger.error(f"Ошибка загрузки ML модели: {error}")
            self._train_default_model()

    def predict(self, text: str) -> Dict:
        """Предсказание категории команд."""
        if self.model is None:
            return {"status": "error", "message": "Модель не загружена"}
        if not isinstance(text, str) or not text.strip():
            return {"status": "error", "message": "Текст команд пуст"}

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
        """Добавление данных и переобучение модели."""
        if not isinstance(category, str) or not category.strip():
            return {"status": "error", "message": "Категории не должны быть пустыми"}
        if not isinstance(examples, list) or not any(isinstance(item, str) and item.strip() for item in examples):
            return {"status": "error", "message": "Нужно передать хотя бы один непустой пример"}

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
            return {"status": "error", "message": "Невозможно обучить модель: недостаточно данных с минимум двумя категориями"}

        try:
            new_model = self._build_model()
            new_model.fit(X, y)
            self.model = new_model
            self.classes = new_model.classes_.tolist()
            self._save_model()
            self.brain.logger.info(f"Добавлены примеры для категории '{category}' и модель переобучена")
            return {"status": "ok", "message": f"Добавлено {len(cleaned_examples)} примеров для '{category}'"}
        except Exception as error:
            self.brain.logger.error(f"Ошибка переобучения модели: {error}")
            return {"status": "error", "message": str(error)}

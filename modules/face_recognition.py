"""
Модуль распознавания лиц JARVIS (стиль Железного Человека)
- Wake-on-face: пробуждение по лицу владельца
- Регистрация лиц пользователей
- Распознавание через камеру
"""

import os
import json
import threading
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

try:
    import face_recognition
    FACE_RECOGNITION_AVAILABLE = True
except ImportError:
    FACE_RECOGNITION_AVAILABLE = False

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False


class FaceRecognition:
    """Модуль распознавания лиц для пробуждения JARVIS."""

    def __init__(self, brain):
        self.brain = brain
        self.logger = brain.logger

        # Конфигурация
        config = brain.config.get("face_recognition", {})
        self.enabled = config.get("enabled", False)
        self.wake_on_face = config.get("wake_on_face", False)
        self.tolerance = config.get("tolerance", 0.6)
        self.camera_id = config.get("camera_id", 0)
        self.recognition_interval = config.get("recognition_interval", 3)  # секунды

        # Хранение лиц
        self.faces_dir = Path("data/faces")
        self.faces_dir.mkdir(parents=True, exist_ok=True)
        self.known_face_encodings: List = []
        self.known_face_names: List[str] = []

        # Состояние
        self.running = False
        self.recognition_thread: Optional[threading.Thread] = None
        self.camera = None
        self.last_recognized: Optional[str] = None
        self.last_recognition_time = 0

        # Загрузка известных лиц
        self._load_known_faces()

    def _load_known_faces(self):
        """Загрузка известных лиц из файлов."""
        if not FACE_RECOGNITION_AVAILABLE or not NUMPY_AVAILABLE:
            return

        faces_file = self.faces_dir / "known_faces.json"
        if faces_file.exists():
            try:
                with open(faces_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                for entry in data:
                    name = entry.get("name")
                    encoding = entry.get("encoding")
                    if name and encoding:
                        self.known_face_names.append(name)
                        self.known_face_encodings.append(encoding)
                self.logger.info(f"Загружено лиц: {len(self.known_face_names)}")
            except Exception as e:
                self.logger.error(f"Ошибка загрузки лиц: {e}")

    def _save_known_faces(self):
        """Сохранение известных лиц в файл."""
        faces_file = self.faces_dir / "known_faces.json"
        try:
            data = []
            for name, encoding in zip(self.known_face_names, self.known_face_encodings):
                data.append({"name": name, "encoding": encoding})
            with open(faces_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.error(f"Ошибка сохранения лиц: {e}")

    def register_face(self, name: str, image_path: Optional[str] = None) -> Dict:
        """Зарегистрировать новое лицо."""
        if not FACE_RECOGNITION_AVAILABLE:
            return {"status": "error", "message": "face_recognition библиотека не установлена"}

        if not CV2_AVAILABLE:
            return {"status": "error", "message": "opencv-python не установлен"}

        try:
            if image_path and Path(image_path).exists():
                image = face_recognition.load_image_file(image_path)
            elif CV2_AVAILABLE:
                # Захват с камеры
                cam = cv2.VideoCapture(self.camera_id)
                ret, frame = cam.read()
                cam.release()
                if not ret:
                    return {"status": "error", "message": "Не удалось захватить изображение с камеры"}
                image = frame
            else:
                return {"status": "error", "message": "Нет источника изображения"}

            encodings = face_recognition.face_encodings(image)
            if not encodings:
                return {"status": "error", "message": "Лицо не обнаружено на изображении"}

            encoding = encodings[0].tolist()  # Преобразуем numpy массив в список для JSON

            # Проверяем дубликаты
            if name in self.known_face_names:
                return {"status": "error", "message": f"Лицо с именем '{name}' уже зарегистрировано"}

            self.known_face_names.append(name)
            self.known_face_encodings.append(encoding)
            self._save_known_faces()

            self.logger.info(f"Зарегистрировано лицо: {name}")
            return {"status": "ok", "message": f"Лицо '{name}' зарегистрировано"}

        except Exception as e:
            self.logger.error(f"Ошибка регистрации лица: {e}")
            return {"status": "error", "message": str(e)}

    def remove_face(self, name: str) -> Dict:
        """Удалить зарегистрированное лицо."""
        if name not in self.known_face_names:
            return {"status": "error", "message": f"Лицо '{name}' не найдено"}

        idx = self.known_face_names.index(name)
        self.known_face_names.pop(idx)
        self.known_face_encodings.pop(idx)
        self._save_known_faces()

        return {"status": "ok", "message": f"Лицо '{name}' удалено"}

    def list_faces(self) -> Dict:
        """Список зарегистрированных лиц."""
        return {
            "status": "ok",
            "faces": self.known_face_names,
            "count": len(self.known_face_names)
        }

    def recognize_frame(self, frame) -> List[Dict]:
        """Распознать лица на кадре."""
        if not FACE_RECOGNITION_AVAILABLE or not NUMPY_AVAILABLE:
            return []

        if not self.known_face_encodings:
            return []

        try:
            # Конвертируем BGR (OpenCV) в RGB (face_recognition)
            rgb_frame = frame[:, :, ::-1]

            # Находим лица
            face_locations = face_recognition.face_locations(rgb_frame)
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

            results = []
            for face_encoding, face_location in zip(face_encodings, face_locations):
                matches = face_recognition.compare_faces(
                    self.known_face_encodings, face_encoding, tolerance=self.tolerance
                )
                name = "Неизвестный"
                confidence = 0.0

                if True in matches:
                    # Находим лучшее совпадение
                    face_distances = face_recognition.face_distance(
                        self.known_face_encodings, face_encoding
                    )
                    best_match_index = face_distances.argmin()
                    if matches[best_match_index]:
                        name = self.known_face_names[best_match_index]
                        confidence = float(1 - face_distances[best_match_index])

                results.append({
                    "name": name,
                    "confidence": confidence,
                    "location": {
                        "top": face_location[0],
                        "right": face_location[1],
                        "bottom": face_location[2],
                        "left": face_location[3]
                    }
                })

            return results

        except Exception as e:
            self.logger.error(f"Ошибка распознавания лица: {e}")
            return []

    def start(self) -> Dict:
        """Запуск мониторинга лиц (пробуждение по лицу)."""
        if not self.enabled:
            return {"status": "error", "message": "Распознавание лиц отключено в конфиге"}

        if not FACE_RECOGNITION_AVAILABLE or not CV2_AVAILABLE:
            return {"status": "error", "message": "Библиотеки для распознавания лиц не установлены"}

        if self.running:
            return {"status": "ok", "message": "Уже запущено"}

        if not self.known_face_encodings:
            return {"status": "error", "message": "Нет зарегистрированных лиц"}

        self.running = True
        self.recognition_thread = threading.Thread(target=self._recognition_loop, daemon=True)
        self.recognition_thread.start()

        self.logger.info("Распознавание лиц запущено")
        return {"status": "ok", "message": "Распознавание лиц запущено"}

    def stop(self) -> Dict:
        """Остановка мониторинга лиц."""
        self.running = False
        if self.recognition_thread:
            self.recognition_thread.join(timeout=2.0)
        if self.camera:
            self.camera.release()
            self.camera = None
        self.logger.info("Распознавание лиц остановлено")
        return {"status": "ok", "message": "Распознавание лиц остановлено"}

    def _recognition_loop(self):
        """Цикл распознавания лиц."""
        self.camera = cv2.VideoCapture(self.camera_id)
        if not self.camera.isOpened():
            self.logger.error("Не удалось открыть камеру")
            self.running = False
            return

        while self.running:
            try:
                ret, frame = self.camera.read()
                if not ret:
                    time.sleep(1)
                    continue

                now = time.time()

                # Распознаем не чаще чем каждые N секунд
                if now - self.last_recognition_time >= self.recognition_interval:
                    results = self.recognize_frame(frame)
                    self.last_recognition_time = now

                    for result in results:
                        name = result["name"]
                        confidence = result["confidence"]

                        if name != "Неизвестный" and confidence > 0.7:
                            if name != self.last_recognized:
                                self.last_recognized = name
                                self.logger.info(f"Распознано лицо: {name} (уверенность: {confidence:.2f})")

                                # Пробуждаем JARVIS
                                if self.wake_on_face and hasattr(self.brain, 'voice_personality'):
                                    self.brain.voice_personality.speak_professional(
                                        f"Обнаружен пользователь {name}. Система активирована, Сэр."
                                    )

                                # Уведомляем brain
                                if hasattr(self.brain, 'on_face_recognized'):
                                    self.brain.on_face_recognized(name, confidence)

                time.sleep(0.5)

            except Exception as e:
                self.logger.error(f"Ошибка в цикле распознавания: {e}")
                time.sleep(1)

        if self.camera:
            self.camera.release()
            self.camera = None

    def take_snapshot(self) -> Dict:
        """Сделать снимок с камеры."""
        if not CV2_AVAILABLE:
            return {"status": "error", "message": "opencv-python не установлен"}

        try:
            cam = cv2.VideoCapture(self.camera_id)
            ret, frame = cam.read()
            cam.release()

            if not ret:
                return {"status": "error", "message": "Не удалось сделать снимок"}

            snapshot_path = self.faces_dir / f"snapshot_{int(time.time())}.jpg"
            cv2.imwrite(str(snapshot_path), frame)

            return {
                "status": "ok",
                "message": "Снимок сохранен",
                "path": str(snapshot_path)
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_status(self) -> Dict:
        """Получить статус распознавания лиц."""
        return {
            "status": "ok",
            "enabled": self.enabled,
            "running": self.running,
            "wake_on_face": self.wake_on_face,
            "faces_count": len(self.known_face_names),
            "faces": self.known_face_names,
            "cv2_available": CV2_AVAILABLE,
            "face_recognition_available": FACE_RECOGNITION_AVAILABLE,
            "tolerance": self.tolerance,
        }

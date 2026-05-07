import json
import os
import random
from dataclasses import dataclass, field, asdict
from typing import List, Optional
from datetime import datetime

DATA_FILE = "tasks_history.json"

# Предопределённые задачи по категориям
PREDEFINED_TASKS = {
    "учёба": [
        "Прочитать статью по программированию",
        "Решить 5 задач на Codewars",
        "Посмотреть лекцию на YouTube",
        "Повторить конспект лекции",
        "Сделать домашнее задание",
        "Прочитать главу учебника",
        "Пройти тест по пройденной теме"
    ],
    "спорт": [
        "Сделать зарядку 15 минут",
        "Пробежать 3 км",
        "Сделать 50 приседаний",
        "Позаниматься йогой 20 минут",
        "Сделать растяжку",
        "Отжаться 30 раз",
        "Покачать пресс 10 минут"
    ],
    "работа": [
        "Ответить на письма",
        "Подготовить отчёт",
        "Созвониться с командой",
        "Проверить дедлайны",
        "Обновить резюме",
        "Изучить новую технологию",
        "Написать документацию"
    ]
}


@dataclass
class Task:
    """Класс, представляющий сгенерированную задачу."""
    task: str
    category: str
    timestamp: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    def validate(self) -> Optional[str]:
        """Проверяет, что задача не пустая."""
        if not self.task or not self.task.strip():
            return "Задача не может быть пустой"
        return None


class TaskGenerator:
    """Управляет генерацией задач, историей и фильтрацией."""

    def __init__(self):
        self.history: List[Task] = []

    def add_custom_task(self, task_text: str, category: str) -> str:
        """Добавляет пользовательскую задачу в историю. Возвращает 'ok' или ошибку."""
        task = Task(task=task_text.strip(), category=category)
        error = task.validate()
        if error:
            return error
        self.history.append(task)
        return "ok"

    def generate_random_task(self, category: str = "все") -> Optional[Task]:
        """
        Генерирует случайную задачу.
        Если категория "все" — выбирает из всех категорий.
        """
        if category == "все":
            # Собираем все задачи
            all_tasks = []
            for tasks in PREDEFINED_TASKS.values():
                all_tasks.extend(tasks)
            if not all_tasks:
                return None
            task_text = random.choice(all_tasks)
            # Определяем категорию выбранной задачи
            for cat, tasks in PREDEFINED_TASKS.items():
                if task_text in tasks:
                    task = Task(task=task_text, category=cat)
                    self.history.append(task)
                    return task
        elif category in PREDEFINED_TASKS:
            tasks = PREDEFINED_TASKS[category]
            if tasks:
                task_text = random.choice(tasks)
                task = Task(task=task_text, category=category)
                self.history.append(task)
                return task
        return None

    def get_filtered_history(self, category_filter: str = "все", search_text: str = "") -> List[Task]:
        """Фильтрует историю по категории и тексту поиска."""
        result = self.history

        if category_filter and category_filter != "все":
            result = [t for t in result if t.category == category_filter]

        if search_text:
            term = search_text.lower()
            result = [t for t in result if term in t.task.lower()]

        return result

    def clear_history(self) -> None:
        """Очищает историю задач."""
        self.history = []

    def save_to_file(self, filename: str = DATA_FILE) -> None:
        """Сохраняет историю в JSON-файл."""
        data = [asdict(t) for t in self.history]
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def load_from_file(self, filename: str = DATA_FILE) -> None:
        """Загружает историю из JSON-файла."""
        if not os.path.exists(filename):
            self.history = []
            return
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.history = [Task(**item) for item in data]
        except (json.JSONDecodeError, KeyError, TypeError):
            self.history = []

    def get_categories(self) -> List[str]:
        """Возвращает список всех категорий."""
        return ["все"] + list(PREDEFINED_TASKS.keys())
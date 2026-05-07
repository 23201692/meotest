import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import json
from models import Task, TaskGenerator, PREDEFINED_TASKS


@pytest.fixture
def generator():
    gen = TaskGenerator()
    return gen


@pytest.fixture
def filled_generator():
    gen = TaskGenerator()
    gen.generate_random_task("учёба")
    gen.generate_random_task("спорт")
    gen.generate_random_task("работа")
    return gen


class TestTask:
    def test_valid_task(self):
        t = Task("Прочитать статью", "учёба")
        assert t.validate() is None

    def test_empty_task(self):
        t = Task("", "учёба")
        assert "не может быть пустой" in t.validate()

    def test_spaces_only_task(self):
        t = Task("   ", "учёба")
        assert "не может быть пустой" in t.validate()


class TestTaskGenerator:
    def test_generate_all_categories(self, generator):
        task = generator.generate_random_task("все")
        assert task is not None
        assert task.task
        assert task.category in PREDEFINED_TASKS
        assert len(generator.history) == 1

    def test_generate_specific_category(self, generator):
        task = generator.generate_random_task("спорт")
        assert task is not None
        assert task.category == "спорт"
        assert task.task in PREDEFINED_TASKS["спорт"]

    def test_add_custom_task_valid(self, generator):
        result = generator.add_custom_task("Моя задача", "работа")
        assert result == "ok"
        assert len(generator.history) == 1
        assert generator.history[0].task == "Моя задача"

    def test_add_custom_task_empty(self, generator):
        result = generator.add_custom_task("", "учёба")
        assert result != "ok"
        assert len(generator.history) == 0

    def test_filter_by_category(self, filled_generator):
        filtered = filled_generator.get_filtered_history(category_filter="спорт")
        assert len(filtered) == 1
        assert filtered[0].category == "спорт"

    def test_filter_all(self, filled_generator):
        filtered = filled_generator.get_filtered_history(category_filter="все")
        assert len(filtered) == 3

    def test_filter_by_search(self, filled_generator):
        # Добавляем задачу с уникальным текстом
        filled_generator.add_custom_task("УНИКАЛЬНЫЙ ТЕКСТ", "учёба")
        filtered = filled_generator.get_filtered_history(search_text="УНИКАЛЬНЫЙ")
        assert len(filtered) == 1

    def test_clear_history(self, filled_generator):
        filled_generator.clear_history()
        assert len(filled_generator.history) == 0

    def test_save_and_load(self, filled_generator, tmp_path):
        file_path = tmp_path / "test_history.json"
        filled_generator.save_to_file(str(file_path))
        new_gen = TaskGenerator()
        new_gen.load_from_file(str(file_path))
        assert len(new_gen.history) == 3

    def test_get_categories(self, generator):
        cats = generator.get_categories()
        assert "все" in cats
        assert "учёба" in cats
        assert "спорт" in cats
        assert "работа" in cats
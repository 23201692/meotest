import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from models import Book, Library


@pytest.fixture
def sample_books():
    return [
        Book("Книга 1", "Автор 1", 2020, "978-1234567890", False),
        Book("Книга 2", "Автор 2", 2019, "978-0987654321", True),
        Book("Книга 3", "Автор 1", 2021, "978-1111111111", False),
    ]


@pytest.fixture
def filled_library(sample_books):
    lib = Library()
    lib.books = sample_books
    return lib


class TestBookValidation:
    def test_valid_book(self):
        b = Book("Название", "Автор", 2023, "978-1234567890")
        assert b.validate() is None

    def test_empty_title(self):
        b = Book("", "Автор", 2023, "978-1234567890")
        assert "Название" in b.validate()

    def test_empty_author(self):
        b = Book("Название", "", 2023, "978-1234567890")
        assert "Автор" in b.validate()

    def test_year_too_small(self):
        b = Book("Название", "Автор", 999, "978-1234567890")
        assert "Год" in b.validate()

    def test_year_too_big(self):
        b = Book("Название", "Автор", 3000, "978-1234567890")
        assert "Год" in b.validate()

    def test_isbn_invalid_chars(self):
        b = Book("Название", "Автор", 2023, "978-12345*890")
        assert "ISBN" in b.validate()

    def test_isbn_too_short(self):
        b = Book("Название", "Автор", 2023, "123")
        assert "ISBN" in b.validate()


class TestLibrary:
    def test_add_valid_book(self):
        lib = Library()
        b = Book("Книга", "Автор", 2020, "978-1234567890")
        assert lib.add_book(b) == "ok"
        assert len(lib.books) == 1

    def test_add_invalid_book(self):
        lib = Library()
        b = Book("", "Автор", 2020, "978-1234567890")
        assert lib.add_book(b) != "ok"
        assert len(lib.books) == 0

    def test_delete_book(self, filled_library):
        assert len(filled_library.books) == 3
        filled_library.delete_book(0)
        assert len(filled_library.books) == 2

    def test_delete_invalid_index(self, filled_library):
        result = filled_library.delete_book(10)
        assert result == False
        assert len(filled_library.books) == 3

    def test_toggle_read(self, filled_library):
        assert filled_library.books[0].read == False
        filled_library.toggle_read(0)
        assert filled_library.books[0].read == True

    def test_filter_by_search(self, filled_library):
        result = filled_library.get_filtered_books(search_term="Книга 1")
        assert len(result) == 1

    def test_filter_by_read(self, filled_library):
        result = filled_library.get_filtered_books(read_filter=True)
        assert len(result) == 1
        assert result[0].read == True

    def test_save_and_load(self, filled_library, tmp_path):
        file_path = tmp_path / "test.json"
        filled_library.save_to_file(str(file_path))
        new_lib = Library()
        new_lib.load_from_file(str(file_path))
        assert len(new_lib.books) == 3

    def test_seed_random(self):
        lib = Library()
        lib.seed_random_books(5)
        assert len(lib.books) == 5
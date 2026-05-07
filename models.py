import json
import os
import random
from dataclasses import dataclass, asdict
from typing import List, Optional

DATA_FILE = "library_data.json"


@dataclass
class Book:
    title: str
    author: str
    year: int
    isbn: str
    read: bool = False

    def validate(self) -> Optional[str]:
        if not self.title or not self.title.strip():
            return "Название книги не может быть пустым"
        if not self.author or not self.author.strip():
            return "Автор не может быть пустым"
        if not isinstance(self.year, int):
            return "Год должен быть целым числом"
        if self.year < 1000 or self.year > 2026:
            return "Год должен быть от 1000 до 2026"
        if not self.isbn or not self.isbn.strip():
            return "ISBN не может быть пустым"
        clean = self.isbn.replace('-', '').replace(' ', '')
        if len(clean) < 10 or len(clean) > 17:
            return "ISBN должен содержать от 10 до 17 символов"
        for c in clean:
            if not c.isdigit() and c != 'X':
                return "ISBN содержит недопустимые символы"
        return None


class Library:
    def __init__(self):
        self.books: List[Book] = []

    def add_book(self, book: Book) -> str:
        error = book.validate()
        if error:
            return error
        self.books.append(book)
        return "ok"

    def delete_book(self, index: int) -> bool:
        if 0 <= index < len(self.books):
            del self.books[index]
            return True
        return False

    def toggle_read(self, index: int) -> bool:
        if 0 <= index < len(self.books):
            self.books[index].read = not self.books[index].read
            return True
        return False

    def get_filtered_books(self, search_term: str = "", read_filter: Optional[bool] = None) -> List[Book]:
        result = self.books
        if search_term:
            term = search_term.lower()
            result = [b for b in result if term in b.title.lower() or term in b.isbn]
        if read_filter is not None:
            result = [b for b in result if b.read == read_filter]
        return result

    def save_to_file(self, filename: str = DATA_FILE) -> None:
        data = [asdict(b) for b in self.books]
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def load_from_file(self, filename: str = DATA_FILE) -> None:
        if not os.path.exists(filename):
            self.books = []
            return
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.books = [Book(**item) for item in data]
        except (json.JSONDecodeError, KeyError, TypeError):
            self.books = []

    def seed_random_books(self, count: int = 5) -> None:
        titles = ["Война и мир", "1984", "Мастер и Маргарита", "Три товарища",
                  "Преступление и наказание", "Великий Гэтсби", "Хоббит"]
        authors = ["Толстой", "Оруэлл", "Булгаков", "Ремарк", "Достоевский",
                   "Фицджеральд", "Толкин"]
        for _ in range(count):
            book = Book(
                title=random.choice(titles),
                author=random.choice(authors),
                year=random.randint(1800, 2025),
                isbn=f"978-{random.randint(1000000000, 9999999999)}",
                read=random.choice([True, False])
            )
            self.add_book(book)

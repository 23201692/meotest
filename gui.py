import tkinter as tk
from tkinter import ttk, messagebox
from models import Library, Book


class LibraryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("meotest - Менеджер библиотеки")
        self.root.geometry("900x600")

        self.library = Library()
        self.library.load_from_file()

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self.on_filter_change)

        self.read_filter_var = tk.StringVar(value="Все")
        self.read_filter_var.trace_add("write", self.on_filter_change)

        self.setup_ui()
        self.refresh_list()

    def setup_ui(self):
        left_frame = ttk.Frame(self.root, padding="10")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH)

        right_frame = ttk.Frame(self.root, padding="10")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # --- Форма добавления ---
        add_frame = ttk.LabelFrame(left_frame, text="Добавить книгу", padding="10")
        add_frame.pack(fill=tk.X, pady=5)

        ttk.Label(add_frame, text="Название:").grid(row=0, column=0, sticky=tk.W)
        self.title_entry = ttk.Entry(add_frame, width=30)
        self.title_entry.grid(row=0, column=1, pady=2)

        ttk.Label(add_frame, text="Автор:").grid(row=1, column=0, sticky=tk.W)
        self.author_entry = ttk.Entry(add_frame, width=30)
        self.author_entry.grid(row=1, column=1, pady=2)

        ttk.Label(add_frame, text="Год:").grid(row=2, column=0, sticky=tk.W)
        self.year_entry = ttk.Entry(add_frame, width=30)
        self.year_entry.grid(row=2, column=1, pady=2)

        ttk.Label(add_frame, text="ISBN:").grid(row=3, column=0, sticky=tk.W)
        self.isbn_entry = ttk.Entry(add_frame, width=30)
        self.isbn_entry.grid(row=3, column=1, pady=2)

        ttk.Button(add_frame, text="Добавить книгу", command=self.add_book).grid(
            row=4, column=0, columnspan=2, pady=10
        )
        ttk.Button(add_frame, text="Добавить 10 случайных книг", command=self.seed_random).grid(
            row=5, column=0, columnspan=2
        )

        # --- Фильтры ---
        filter_frame = ttk.LabelFrame(left_frame, text="Фильтры", padding="10")
        filter_frame.pack(fill=tk.X, pady=5)

        ttk.Label(filter_frame, text="Поиск (название/ISBN):").pack(anchor=tk.W)
        ttk.Entry(filter_frame, textvariable=self.search_var, width=30).pack(fill=tk.X, pady=2)

        ttk.Label(filter_frame, text="Статус чтения:").pack(anchor=tk.W)
        ttk.Combobox(
            filter_frame,
            textvariable=self.read_filter_var,
            values=["Все", "Прочитано", "Не прочитано"],
            state="readonly",
            width=27
        ).pack(fill=tk.X, pady=2)

        # --- Кнопки сохранения/загрузки ---
        io_frame = ttk.Frame(left_frame)
        io_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=10)
        ttk.Button(io_frame, text="Сохранить в JSON", command=self.save_data).pack(side=tk.LEFT, padx=5)
        ttk.Button(io_frame, text="Загрузить из JSON", command=self.load_data).pack(side=tk.LEFT, padx=5)

        # --- Список книг ---
        list_frame = ttk.Frame(right_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("title", "author", "year", "isbn", "read")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", selectmode="browse")

        self.tree.heading("title", text="Название")
        self.tree.heading("author", text="Автор")
        self.tree.heading("year", text="Год")
        self.tree.heading("isbn", text="ISBN")
        self.tree.heading("read", text="Прочитана")

        self.tree.column("title", width=200)
        self.tree.column("author", width=150)
        self.tree.column("year", width=60, anchor=tk.CENTER)
        self.tree.column("isbn", width=150)
        self.tree.column("read", width=80, anchor=tk.CENTER)

        scrollbar = ttk.Scrollbar(list_frame, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # --- Кнопки действий ---
        action_frame = ttk.Frame(right_frame)
        action_frame.pack(fill=tk.X, pady=5)
        ttk.Button(action_frame, text="Переключить статус", command=self.toggle_read).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Удалить книгу", command=self.delete_book).pack(side=tk.LEFT, padx=5)

    def add_book(self):
        title = self.title_entry.get().strip()
        author = self.author_entry.get().strip()
        year_str = self.year_entry.get().strip()
        isbn = self.isbn_entry.get().strip()

        try:
            year = int(year_str)
        except ValueError:
            messagebox.showerror("Ошибка", "Год должен быть целым числом!")
            return

        book = Book(title=title, author=author, year=year, isbn=isbn)
        result = self.library.add_book(book)

        if result == "ok":
            self.title_entry.delete(0, tk.END)
            self.author_entry.delete(0, tk.END)
            self.year_entry.delete(0, tk.END)
            self.isbn_entry.delete(0, tk.END)
            self.refresh_list()
            messagebox.showinfo("Успех", "Книга добавлена!")
        else:
            messagebox.showerror("Ошибка", result)

    def delete_book(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите книгу для удаления")
            return
        index = int(selected[0])
        self.library.delete_book(index)
        self.refresh_list()

    def toggle_read(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите книгу")
            return
        index = int(selected[0])
        self.library.toggle_read(index)
        self.refresh_list()

    def seed_random(self):
        self.library.seed_random_books(10)
        self.refresh_list()
        messagebox.showinfo("Готово", "Добавлено 10 случайных книг")

    def on_filter_change(self, *args):
        self.refresh_list()

    def refresh_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        search = self.search_var.get().strip()
        read_status = self.read_filter_var.get()

        read_filter = None
        if read_status == "Прочитано":
            read_filter = True
        elif read_status == "Не прочитано":
            read_filter = False

        filtered = self.library.get_filtered_books(search_term=search, read_filter=read_filter)
        index_map = {id(b): i for i, b in enumerate(self.library.books)}

        for book in filtered:
            idx = index_map[id(book)]
            read_text = "Да" if book.read else "Нет"
            self.tree.insert(
                "", tk.END, iid=str(idx),
                values=(book.title, book.author, book.year, book.isbn, read_text)
            )

    def save_data(self):
        try:
            self.library.save_to_file()
            messagebox.showinfo("Сохранено", "Данные сохранены в library_data.json")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить: {e}")

    def load_data(self):
        self.library.load_from_file()
        self.refresh_list()
        messagebox.showinfo("Загружено", "Данные загружены из library_data.json")


def run_gui():
    root = tk.Tk()
    app = LibraryApp(root)
    root.mainloop()

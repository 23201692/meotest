import tkinter as tk
from tkinter import ttk, messagebox
from models import TaskGenerator


class TaskGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Random Task Generator")
        self.root.geometry("800x600")

        self.generator = TaskGenerator()
        self.generator.load_from_file()

        # Переменные для фильтров
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self.on_filter_change)

        self.category_filter_var = tk.StringVar(value="все")
        self.category_filter_var.trace_add("write", self.on_filter_change)

        self.setup_ui()
        self.refresh_list()

    def setup_ui(self):
        # Левый фрейм (управление)
        left_frame = ttk.Frame(self.root, padding="10")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH)

        # Правый фрейм (список)
        right_frame = ttk.Frame(self.root, padding="10")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # --- Генерация задачи ---
        gen_frame = ttk.LabelFrame(left_frame, text="Сгенерировать задачу", padding="10")
        gen_frame.pack(fill=tk.X, pady=5)

        ttk.Label(gen_frame, text="Категория:").pack(anchor=tk.W)
        self.gen_category = ttk.Combobox(
            gen_frame,
            values=self.generator.get_categories(),
            state="readonly",
            width=27
        )
        self.gen_category.set("все")
        self.gen_category.pack(fill=tk.X, pady=2)

        ttk.Button(gen_frame, text="🎲 Сгенерировать задачу", command=self.generate_task).pack(fill=tk.X, pady=10)

        # --- Последняя сгенерированная ---
        last_frame = ttk.LabelFrame(left_frame, text="Последняя задача", padding="10")
        last_frame.pack(fill=tk.X, pady=5)

        self.last_task_label = ttk.Label(last_frame, text="Нажмите кнопку...", wraplength=250, font=("Arial", 11))
        self.last_task_label.pack(fill=tk.X)

        # --- Добавление своей задачи ---
        add_frame = ttk.LabelFrame(left_frame, text="Добавить свою задачу", padding="10")
        add_frame.pack(fill=tk.X, pady=5)

        ttk.Label(add_frame, text="Текст задачи:").pack(anchor=tk.W)
        self.task_entry = ttk.Entry(add_frame, width=30)
        self.task_entry.pack(fill=tk.X, pady=2)

        ttk.Label(add_frame, text="Категория:").pack(anchor=tk.W)
        self.add_category = ttk.Combobox(
            add_frame,
            values=list(self.generator.get_categories())[1:],  # без "все"
            state="readonly",
            width=27
        )
        self.add_category.set("учёба")
        self.add_category.pack(fill=tk.X, pady=2)

        ttk.Button(add_frame, text="➕ Добавить задачу", command=self.add_custom_task).pack(fill=tk.X, pady=5)

        # --- Фильтры ---
        filter_frame = ttk.LabelFrame(left_frame, text="Фильтры истории", padding="10")
        filter_frame.pack(fill=tk.X, pady=5)

        ttk.Label(filter_frame, text="Поиск:").pack(anchor=tk.W)
        ttk.Entry(filter_frame, textvariable=self.search_var, width=30).pack(fill=tk.X, pady=2)

        ttk.Label(filter_frame, text="Категория:").pack(anchor=tk.W)
        ttk.Combobox(
            filter_frame,
            textvariable=self.category_filter_var,
            values=self.generator.get_categories(),
            state="readonly",
            width=27
        ).pack(fill=tk.X, pady=2)

        # --- Кнопки сохранения/очистки ---
        btn_frame = ttk.Frame(left_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        ttk.Button(btn_frame, text="💾 Сохранить", command=self.save_data).pack(side=tk.LEFT, padx=2, expand=True, fill=tk.X)
        ttk.Button(btn_frame, text="📂 Загрузить", command=self.load_data).pack(side=tk.LEFT, padx=2, expand=True, fill=tk.X)
        ttk.Button(btn_frame, text="🗑 Очистить", command=self.clear_history).pack(side=tk.LEFT, padx=2, expand=True, fill=tk.X)

        # --- Таблица с историей ---
        list_frame = ttk.Frame(right_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("task", "category", "timestamp")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", selectmode="browse")

        self.tree.heading("task", text="Задача")
        self.tree.heading("category", text="Категория")
        self.tree.heading("timestamp", text="Время")

        self.tree.column("task", width=350)
        self.tree.column("category", width=100, anchor=tk.CENTER)
        self.tree.column("timestamp", width=150, anchor=tk.CENTER)

        scrollbar = ttk.Scrollbar(list_frame, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def generate_task(self):
        category = self.gen_category.get()
        task = self.generator.generate_random_task(category)

        if task:
            self.last_task_label.config(text=f"[{task.category}] {task.task}")
            self.refresh_list()
        else:
            messagebox.showwarning("Ошибка", "Нет задач в выбранной категории")

    def add_custom_task(self):
        task_text = self.task_entry.get()
        category = self.add_category.get()

        if not category:
            messagebox.showerror("Ошибка", "Выберите категорию")
            return

        result = self.generator.add_custom_task(task_text, category)

        if result == "ok":
            self.task_entry.delete(0, tk.END)
            self.last_task_label.config(text=f"[{category}] {task_text}")
            self.refresh_list()
            messagebox.showinfo("Успех", "Задача добавлена!")
        else:
            messagebox.showerror("Ошибка", result)

    def on_filter_change(self, *args):
        self.refresh_list()

    def refresh_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        search = self.search_var.get().strip()
        category = self.category_filter_var.get()

        filtered = self.generator.get_filtered_history(category_filter=category, search_text=search)

        for i, task in enumerate(filtered):
            self.tree.insert("", tk.END, iid=str(i),
                           values=(task.task, task.category, task.timestamp))

    def save_data(self):
        try:
            self.generator.save_to_file()
            messagebox.showinfo("Сохранено", "История сохранена в tasks_history.json")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def load_data(self):
        self.generator.load_from_file()
        self.refresh_list()
        messagebox.showinfo("Загружено", "История загружена")

    def clear_history(self):
        if messagebox.askyesno("Подтверждение", "Удалить всю историю?"):
            self.generator.clear_history()
            self.refresh_list()
            self.last_task_label.config(text="Нажмите кнопку...")


def run_gui():
    root = tk.Tk()
    app = TaskGeneratorApp(root)
    root.mainloop()
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import json
import os

DATA_FILE = "expenses.json"

class ExpenseTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker - Трекер расходов")
        self.root.geometry("800x500")
        
        # Список для хранения расходов
        self.expenses = []
        self.load_data()
        
        # Создание GUI
        self.create_input_frame()
        self.create_table_frame()
        self.create_filter_frame()
        self.create_stats_frame()
        
        # Обновление таблицы
        self.refresh_table()
    
    def create_input_frame(self):
        """Форма для добавления расходов"""
        input_frame = tk.LabelFrame(self.root, text="Добавить расход", padx=10, pady=10)
        input_frame.pack(fill="x", padx=10, pady=5)
        
        # Поле Сумма
        tk.Label(input_frame, text="Сумма:").grid(row=0, column=0, sticky="w")
        self.amount_entry = tk.Entry(input_frame, width=20)
        self.amount_entry.grid(row=0, column=1, padx=5)
        
        # Поле Категория
        tk.Label(input_frame, text="Категория:").grid(row=0, column=2, sticky="w", padx=(20,0))
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(input_frame, textvariable=self.category_var, 
                                           values=["Еда", "Транспорт", "Развлечения", "Жильё", "Здоровье", "Другое"],
                                           width=15)
        self.category_combo.grid(row=0, column=3, padx=5)
        self.category_combo.set("Еда")
        
        # Поле Дата
        tk.Label(input_frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=4, sticky="w", padx=(20,0))
        self.date_entry = tk.Entry(input_frame, width=12)
        self.date_entry.grid(row=0, column=5, padx=5)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        # Кнопка Добавить
        self.add_btn = tk.Button(input_frame, text="Добавить расход", command=self.add_expense, bg="lightgreen")
        self.add_btn.grid(row=0, column=6, padx=10)
    
    def create_table_frame(self):
        """Таблица со списком расходов"""
        table_frame = tk.LabelFrame(self.root, text="Список расходов", padx=10, pady=10)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Создание таблицы Treeview
        columns = ("ID", "Сумма", "Категория", "Дата")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)
        
        # Настройка колонок
        self.tree.heading("ID", text="ID")
        self.tree.heading("Сумма", text="Сумма (₽)")
        self.tree.heading("Категория", text="Категория")
        self.tree.heading("Дата", text="Дата")
        
        self.tree.column("ID", width=50)
        self.tree.column("Сумма", width=100)
        self.tree.column("Категория", width=120)
        self.tree.column("Дата", width=100)
        
        # Скроллбар
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def create_filter_frame(self):
        """Фильтрация расходов"""
        filter_frame = tk.LabelFrame(self.root, text="Фильтрация", padx=10, pady=10)
        filter_frame.pack(fill="x", padx=10, pady=5)
        
        # Фильтр по категории
        tk.Label(filter_frame, text="Категория:").grid(row=0, column=0, sticky="w")
        self.filter_category_var = tk.StringVar(value="Все")
        self.filter_category_combo = ttk.Combobox(filter_frame, textvariable=self.filter_category_var,
                                                  values=["Все", "Еда", "Транспорт", "Развлечения", "Жильё", "Здоровье", "Другое"],
                                                  width=15)
        self.filter_category_combo.grid(row=0, column=1, padx=5)
        
        # Фильтр по дате (начало)
        tk.Label(filter_frame, text="Дата от (ГГГГ-ММ-ДД):").grid(row=0, column=2, sticky="w", padx=(20,0))
        self.filter_date_from = tk.Entry(filter_frame, width=12)
        self.filter_date_from.grid(row=0, column=3, padx=5)
        
        # Фильтр по дате (конец)
        tk.Label(filter_frame, text="до:").grid(row=0, column=4, sticky="w")
        self.filter_date_to = tk.Entry(filter_frame, width=12)
        self.filter_date_to.grid(row=0, column=5, padx=5)
        
        # Кнопка Применить фильтр
        self.filter_btn = tk.Button(filter_frame, text="Применить фильтр", command=self.apply_filter, bg="lightblue")
        self.filter_btn.grid(row=0, column=6, padx=10)
        
        # Кнопка Сбросить фильтр
        self.reset_filter_btn = tk.Button(filter_frame, text="Сбросить", command=self.reset_filter)
        self.reset_filter_btn.grid(row=0, column=7, padx=5)
    
    def create_stats_frame(self):
        """Статистика: сумма расходов за период"""
        stats_frame = tk.LabelFrame(self.root, text="Статистика", padx=10, pady=10)
        stats_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Label(stats_frame, text="Сумма расходов за выбранный период:").pack(side="left")
        self.total_label = tk.Label(stats_frame, text="0 ₽", font=("Arial", 12, "bold"), fg="red")
        self.total_label.pack(side="left", padx=10)
        
        # Кнопка подсчёта суммы
        self.calc_btn = tk.Button(stats_frame, text="Подсчитать сумму за период", command=self.calculate_total, bg="orange")
        self.calc_btn.pack(side="right", padx=10)
    
    def add_expense(self):
        """Добавление нового расхода"""
        try:
            # Проверка суммы
            amount_str = self.amount_entry.get().strip()
            if not amount_str:
                messagebox.showerror("Ошибка", "Введите сумму!")
                return
            amount = float(amount_str)
            if amount <= 0:
                messagebox.showerror("Ошибка", "Сумма должна быть положительным числом!")
                return
            
            # Получение категории
            category = self.category_var.get()
            
            # Проверка даты
            date_str = self.date_entry.get().strip()
            try:
                datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Ошибка", "Неверный формат даты! Используйте ГГГГ-ММ-ДД")
                return
            
            # Создание ID
            expense_id = len(self.expenses) + 1
            
            # Добавление расхода
            expense = {
                "id": expense_id,
                "amount": amount,
                "category": category,
                "date": date_str
            }
            self.expenses.append(expense)
            
            # Сохранение и обновление
            self.save_data()
            self.refresh_table()
            
            # Очистка полей (сумма)
            self.amount_entry.delete(0, tk.END)
            
            messagebox.showinfo("Успех", "Расход добавлен!")
            
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректное число в поле 'Сумма'!")
    
    def save_data(self):
        """Сохранение данных в JSON"""
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(self.expenses, f, ensure_ascii=False, indent=4)
    
    def load_data(self):
        """Загрузка данных из JSON"""
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    self.expenses = json.load(f)
            except:
                self.expenses = []
        else:
            self.expenses = []
    
    def refresh_table(self, filtered_expenses=None):
        """Обновление таблицы"""
        # Очистка таблицы
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        # Отображение расходов
        expenses_to_show = filtered_expenses if filtered_expenses is not None else self.expenses
        for exp in expenses_to_show:
            self.tree.insert("", "end", values=(exp["id"], exp["amount"], exp["category"], exp["date"]))
    
    def apply_filter(self):
        """Применение фильтров"""
        filtered = self.expenses.copy()
        
        # Фильтр по категории
        category_filter = self.filter_category_var.get()
        if category_filter != "Все":
            filtered = [e for e in filtered if e["category"] == category_filter]
        
        # Фильтр по дате (начало)
        date_from = self.filter_date_from.get().strip()
        if date_from:
            try:
                from_date = datetime.strptime(date_from, "%Y-%m-%d")
                filtered = [e for e in filtered if datetime.strptime(e["date"], "%Y-%m-%d") >= from_date]
            except ValueError:
                messagebox.showerror("Ошибка", "Неверный формат даты 'от'!")
                return
        
        # Фильтр по дате (конец)
        date_to = self.filter_date_to.get().strip()
        if date_to:
            try:
                to_date = datetime.strptime(date_to, "%Y-%m-%d")
                filtered = [e for e in filtered if datetime.strptime(e["date"], "%Y-%m-%d") <= to_date]
            except ValueError:
                messagebox.showerror("Ошибка", "Неверный формат даты 'до'!")
                return
        
        self.refresh_table(filtered)
    
    def reset_filter(self):
        """Сброс фильтров"""
        self.filter_category_var.set("Все")
        self.filter_date_from.delete(0, tk.END)
        self.filter_date_to.delete(0, tk.END)
        self.refresh_table()
    
    def calculate_total(self):
        """Подсчёт суммы расходов за выбранный период"""
        # Получаем текущие отфильтрованные данные из таблицы
        current_items = []
        for item in self.tree.get_children():
            values = self.tree.item(item)["values"]
            if values:
                current_items.append({
                    "amount": values[1],
                    "date": values[3]
                })
        
        if not current_items:
            messagebox.showinfo("Информация", "Нет расходов за выбранный период.")
            self.total_label.config(text="0 ₽")
            return
        
        total = sum(item["amount"] for item in current_items)
        self.total_label.config(text=f"{total:.2f} ₽")
        messagebox.showinfo("Статистика", f"Общая сумма расходов за выбранный период: {total:.2f} ₽")

if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTracker(root)
    root.mainloop()

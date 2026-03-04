import sqlite3
import pandas as pd
from datetime import datetime
from pathlib import Path

class Database:
    """Класс для работы с базой данных сотрудников"""
    
    def __init__(self, db_path="data/employees.db"):
        """
        Инициализация подключения к БД
        
        Параметры:
        db_path (str): путь к файлу базы данных
        """
        # Создаем папку data, если её нет
        Path("data").mkdir(exist_ok=True)
        
        self.db_path = db_path
        self.connection = None
        self.connect()
        self.create_tables()
        
        # Если таблицы пустые, добавляем тестовые данные
        if self.is_tables_empty():
            self.add_test_data()
    
    def connect(self):
        """Установка соединения с БД"""
        self.connection = sqlite3.connect(self.db_path)
        # Для работы с pandas как словарь
        self.connection.row_factory = sqlite3.Row
    
    def create_tables(self):
        """Создание необходимых таблиц"""
        cursor = self.connection.cursor()
        
        # Таблица отделов
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS departments (
                department_id INTEGER PRIMARY KEY AUTOINCREMENT,
                department_name TEXT NOT NULL UNIQUE
            )
        """)
        
        # Таблица сотрудников
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                employee_id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                department_id INTEGER,
                position TEXT,
                hire_date TEXT NOT NULL,
                salary REAL NOT NULL,
                is_active INTEGER DEFAULT 1,
                FOREIGN KEY (department_id) REFERENCES departments (department_id)
            )
        """)
        
        self.connection.commit()
    
    def is_tables_empty(self):
        """Проверка, пустые ли таблицы"""
        cursor = self.connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM employees")
        count = cursor.fetchone()[0]
        return count == 0
    
    def add_test_data(self):
        """Добавление тестовых данных"""
        cursor = self.connection.cursor()
        
        # Добавление отделов
        departments = ['HR', 'IT', 'Sales', 'Marketing', 'Finance', 'Production']
        for dept in departments:
            cursor.execute(
                "INSERT OR IGNORE INTO departments (department_name) VALUES (?)",
                (dept,)
            )
        
        # Получаем ID отделов
        cursor.execute("SELECT department_id, department_name FROM departments")
        dept_ids = {row[1]: row[0] for row in cursor.fetchall()}
        
        # Тестовые сотрудники
        employees = [
            ('Иванов Иван Иванович', dept_ids['IT'], 'Senior Developer', '2022-01-15', 120000),
            ('Петров Петр Петрович', dept_ids['IT'], 'Junior Developer', '2023-08-20', 60000),
            ('Сидорова Анна Сергеевна', dept_ids['HR'], 'HR Manager', '2021-03-10', 80000),
            ('Козлов Дмитрий Андреевич', dept_ids['Sales'], 'Sales Manager', '2023-10-01', 70000),
            ('Морозова Елена Владимировна', dept_ids['Marketing'], 'Marketing Specialist', '2022-11-15', 65000),
            ('Волков Алексей Игоревич', dept_ids['IT'], 'Team Lead', '2020-05-20', 150000),
            ('Зайцева Ольга Павловна', dept_ids['Finance'], 'Accountant', '2022-09-01', 75000),
            ('Соколов Андрей Викторович', dept_ids['Sales'], 'Sales Representative', '2023-07-10', 55000),
            ('Лебедева Татьяна Михайловна', dept_ids['HR'], 'Recruiter', '2023-09-05', 50000),
            ('Новиков Павел Сергеевич', dept_ids['Production'], 'Production Manager', '2021-12-01', 85000),
            ('Григорьева Наталья Александровна', dept_ids['Marketing'], 'SMM Manager', '2023-06-15', 45000),
            ('Федоров Михаил Дмитриевич', dept_ids['IT'], 'DevOps Engineer', '2022-04-10', 130000),
            ('Павлова Екатерина Игоревна', dept_ids['Finance'], 'Financial Analyst', '2022-08-22', 70000),
            ('Степанов Роман Викторович', dept_ids['Sales'], 'Senior Sales Manager', '2021-07-01', 90000),
            ('Николаева Светлана Петровна', dept_ids['Production'], 'Quality Control', '2023-11-01', 48000),
        ]
        
        for emp in employees:
            cursor.execute("""
                INSERT INTO employees (full_name, department_id, position, hire_date, salary, is_active)
                VALUES (?, ?, ?, ?, ?, 1)
            """, emp)
        
        self.connection.commit()
        print("✅ Тестовые данные добавлены")
    
    def get_all_employees(self):
        """
        Получение всех активных сотрудников с названиями отделов
        
        Возвращает:
        pd.DataFrame: данные о сотрудниках
        """
        query = """
            SELECT 
                e.employee_id,
                e.full_name,
                d.department_name,
                e.position,
                e.hire_date,
                e.salary,
                e.is_active
            FROM employees e
            LEFT JOIN departments d ON e.department_id = d.department_id
            WHERE e.is_active = 1
            ORDER BY e.full_name
        """
        return pd.read_sql_query(query, self.connection)
    
    def get_employee_by_id(self, employee_id):
        """Получение данных конкретного сотрудника"""
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT 
                e.employee_id,
                e.full_name,
                e.department_id,
                d.department_name,
                e.position,
                e.hire_date,
                e.salary
            FROM employees e
            LEFT JOIN departments d ON e.department_id = d.department_id
            WHERE e.employee_id = ?
        """, (employee_id,))
        
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None
    
    def add_employee(self, full_name, department_id, position, hire_date, salary):
        """Добавление нового сотрудника"""
        cursor = self.connection.cursor()
        cursor.execute("""
            INSERT INTO employees (full_name, department_id, position, hire_date, salary)
            VALUES (?, ?, ?, ?, ?)
        """, (full_name, department_id, position, hire_date, salary))
        self.connection.commit()
        return cursor.lastrowid
    
    def update_employee(self, employee_id, full_name, department_id, position, hire_date, salary):
        """Обновление данных сотрудника"""
        cursor = self.connection.cursor()
        cursor.execute("""
            UPDATE employees 
            SET full_name = ?, department_id = ?, position = ?, hire_date = ?, salary = ?
            WHERE employee_id = ?
        """, (full_name, department_id, position, hire_date, salary, employee_id))
        self.connection.commit()
    
    def delete_employee(self, employee_id):
        """Удаление сотрудника (помечаем is_active = 0)"""
        cursor = self.connection.cursor()
        cursor.execute(
            "UPDATE employees SET is_active = 0 WHERE employee_id = ?",
            (employee_id,)
        )
        self.connection.commit()
    
    def get_departments(self):
        """Получение списка всех отделов"""
        cursor = self.connection.cursor()
        cursor.execute("SELECT department_id, department_name FROM departments ORDER BY department_name")
        return [{"id": row[0], "name": row[1]} for row in cursor.fetchall()]
    
    def get_department_name_by_id(self, department_id):
        """Получение названия отдела по ID"""
        cursor = self.connection.cursor()
        cursor.execute("SELECT department_name FROM departments WHERE department_id = ?", (department_id,))
        result = cursor.fetchone()
        return result[0] if result else "Не указан"
    
    def close(self):
        """Закрытие соединения с БД"""
        if self.connection:
            self.connection.close()

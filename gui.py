import sys
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from datetime import datetime
import pandas as pd

from database import Database
from models import Employee
from analytics import DataAnalyzer
from visualization import Plotter

class HRApp(QMainWindow):
    """
    Главный класс графического интерфейса
    Соответствует описанию в диаграмме классов
    """
    
    def __init__(self):
        super().__init__()
        
        # Инициализация БД и анализатора
        self.db = Database()
        self.analyzer = DataAnalyzer()
        self.current_employee = None
        
        # Настройка окна
        self.setWindowTitle("Учет персонала - Кадровое приложение")
        self.setGeometry(100, 100, 1200, 700)
        
        # Установка стиля (ЧЕРНО-БЕЛАЯ ТЕМА)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QPushButton {
                background-color: #ffffff;
                color: #000000;
                border: 2px solid #000000;
                padding: 8px 15px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            QPushButton:pressed {
                background-color: #c0c0c0;
            }
            QPushButton:disabled {
                background-color: #f0f0f0;
                border: 2px solid #a0a0a0;
                color: #a0a0a0;
            }
            QTableWidget {
                background-color: white;
                border: 1px solid #000000;
                gridline-color: #000000;
                color: #000000;
            }
            QTableWidget::item {
                padding: 5px;
                color: #000000;
            }
            QHeaderView::section {
                background-color: #333333;
                color: white;
                padding: 5px;
                border: 1px solid #000000;
                font-weight: bold;
            }
            QTabWidget::pane {
                border: 1px solid #000000;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #e0e0e0;
                color: #000000;
                padding: 8px 15px;
                margin-right: 2px;
                border: 1px solid #000000;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: white;
                color: #000000;
                border-bottom: 1px solid white;
            }
            QTabBar::tab:hover {
                background-color: #d0d0d0;
            }
            QLabel {
                color: #000000;
            }
            QLineEdit {
                border: 1px solid #000000;
                padding: 5px;
                border-radius: 3px;
                background-color: white;
                color: #000000;
            }
            QLineEdit:focus {
                border: 2px solid #000000;
            }
            QComboBox {
                border: 1px solid #000000;
                padding: 5px;
                border-radius: 3px;
                background-color: white;
                color: #000000;
            }
            QComboBox:hover {
                background-color: #f0f0f0;
            }
            QComboBox::drop-down {
                border-left: 1px solid #000000;
            }
            QGroupBox {
                border: 2px solid #000000;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                color: #000000;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QTextEdit {
                border: 1px solid #000000;
                background-color: white;
                color: #000000;
            }
            QDateEdit {
                border: 1px solid #000000;
                padding: 5px;
                border-radius: 3px;
                background-color: white;
                color: #000000;
            }
        """)
        
        # Создание интерфейса
        self.setup_ui()
        
        # Загрузка данных
        self.refresh_data()
    
    def setup_ui(self):
        """Создание пользовательского интерфейса"""
        
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Основной layout
        main_layout = QVBoxLayout(central_widget)
        
        # Верхняя панель с кнопками
        toolbar = self.create_toolbar()
        main_layout.addLayout(toolbar)
        
        # Табы
        self.tabs = QTabWidget()
        
        # Таб со списком сотрудников
        self.employees_tab = self.create_employees_tab()
        self.tabs.addTab(self.employees_tab, "👥 Сотрудники")
        
        # Таб с аналитикой
        self.analytics_tab = self.create_analytics_tab()
        self.tabs.addTab(self.analytics_tab, "📊 Аналитика")
        
        # Таб с отчетами
        self.reports_tab = self.create_reports_tab()
        self.tabs.addTab(self.reports_tab, "📈 Отчеты")
        
        main_layout.addWidget(self.tabs)
    
    def create_toolbar(self):
        """Создание панели инструментов"""
        toolbar = QHBoxLayout()
        
        # Кнопки
        self.add_btn = QPushButton("➕ Добавить сотрудника")
        self.add_btn.clicked.connect(self.add_employee)
        
        self.edit_btn = QPushButton("✏️ Редактировать")
        self.edit_btn.clicked.connect(self.edit_employee)
        self.edit_btn.setEnabled(False)
        
        self.delete_btn = QPushButton("🗑️ Удалить")
        self.delete_btn.clicked.connect(self.delete_employee)
        self.delete_btn.setEnabled(False)
        
        self.refresh_btn = QPushButton("🔄 Обновить")
        self.refresh_btn.clicked.connect(self.refresh_data)
        
        # Поиск
        self.search_label = QLabel("🔍 Поиск:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Введите имя сотрудника...")
        self.search_input.textChanged.connect(self.filter_employees)
        
        # Фильтр по отделам
        self.filter_label = QLabel("Отдел:")
        self.department_filter = QComboBox()
        self.department_filter.addItem("Все отделы")
        self.department_filter.currentTextChanged.connect(self.filter_employees)
        
        # Добавляем элементы
        toolbar.addWidget(self.add_btn)
        toolbar.addWidget(self.edit_btn)
        toolbar.addWidget(self.delete_btn)
        toolbar.addWidget(self.refresh_btn)
        toolbar.addStretch()
        toolbar.addWidget(self.search_label)
        toolbar.addWidget(self.search_input)
        toolbar.addWidget(self.filter_label)
        toolbar.addWidget(self.department_filter)
        
        return toolbar
    
    def create_employees_tab(self):
        """Создание вкладки со списком сотрудников"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Таблица сотрудников
        self.employees_table = QTableWidget()
        self.employees_table.setColumnCount(7)
        self.employees_table.setHorizontalHeaderLabels([
            "ID", "ФИО", "Отдел", "Должность", "Дата приема", "Оклад", "Стаж (мес)"
        ])
        
        # Настройка таблицы
        header = self.employees_table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # ФИО растягивается
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        
        # Скрываем ID
        self.employees_table.setColumnHidden(0, True)
        
        # Выделение строк
        self.employees_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.employees_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.employees_table.itemSelectionChanged.connect(self.on_employee_selected)
        
        layout.addWidget(self.employees_table)
        
        return tab
    
    def create_analytics_tab(self):
        """Создание вкладки с аналитикой"""
        tab = QWidget()
        layout = QHBoxLayout(tab)
        
        # Левая панель с кнопками
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Группа аналитических кнопок
        group_box = QGroupBox("Аналитические инструменты")
        group_layout = QVBoxLayout()
        
        self.classify_btn = QPushButton("📊 Классификация по стажу")
        self.classify_btn.clicked.connect(self.show_experience_classification)
        
        self.turnover_btn = QPushButton("⚠️ Анализ текучести")
        self.turnover_btn.clicked.connect(self.show_turnover_analysis)
        
        self.salary_stats_btn = QPushButton("💰 Статистика зарплат")
        self.salary_stats_btn.clicked.connect(self.show_salary_statistics)
        
        self.dept_stats_btn = QPushButton("🏢 Статистика по отделам")
        self.dept_stats_btn.clicked.connect(self.show_department_statistics)
        
        group_layout.addWidget(self.classify_btn)
        group_layout.addWidget(self.turnover_btn)
        group_layout.addWidget(self.salary_stats_btn)
        group_layout.addWidget(self.dept_stats_btn)
        group_layout.addStretch()
        
        group_box.setLayout(group_layout)
        left_layout.addWidget(group_box)
        
        # Правая панель с результатами
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        self.analytics_text = QTextEdit()
        self.analytics_text.setReadOnly(True)
        self.analytics_text.setFont(QFont("Courier", 10))
        
        right_layout.addWidget(self.analytics_text)
        
        # Добавляем панели в layout
        layout.addWidget(left_panel, 1)
        layout.addWidget(right_panel, 2)
        
        return tab
    
    def create_reports_tab(self):
        """Создание вкладки с отчетами и графиками"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Панель с кнопками
        button_panel = QHBoxLayout()
        
        self.salary_plot_btn = QPushButton("📊 Распределение зарплат")
        self.salary_plot_btn.clicked.connect(self.plot_salary_distribution)
        
        self.dept_plot_btn = QPushButton("🥧 Структура по отделам")
        self.dept_plot_btn.clicked.connect(self.plot_department_structure)
        
        self.turnover_plot_btn = QPushButton("📉 Анализ текучести")
        self.turnover_plot_btn.clicked.connect(self.plot_turnover_risk)
        
        self.trend_plot_btn = QPushButton("📈 Динамика приема")
        self.trend_plot_btn.clicked.connect(self.plot_turnover_trend)
        
        button_panel.addWidget(self.salary_plot_btn)
        button_panel.addWidget(self.dept_plot_btn)
        button_panel.addWidget(self.turnover_plot_btn)
        button_panel.addWidget(self.trend_plot_btn)
        button_panel.addStretch()
        
        layout.addLayout(button_panel)
        
        # Холст для графиков
        self.plot_widget = QWidget()
        plot_layout = QVBoxLayout(self.plot_widget)
        
        self.plotter = Plotter(self.plot_widget, width=10, height=6)
        plot_layout.addWidget(self.plotter)
        
        layout.addWidget(self.plot_widget)
        
        return tab
    
    def refresh_data(self):
        """Обновление данных в таблице"""
        # Получаем данные из БД
        self.employees_df = self.db.get_all_employees()
        
        # Обновляем анализатор
        self.analyzer.set_data(self.employees_df)
        
        # Обновляем фильтр отделов
        self.update_department_filter()
        
        # Заполняем таблицу
        self.populate_employees_table()
        
        # Сбрасываем выделение
        self.current_employee = None
        self.edit_btn.setEnabled(False)
        self.delete_btn.setEnabled(False)
    
    def update_department_filter(self):
        """Обновление списка отделов в фильтре"""
        current_text = self.department_filter.currentText()
        
        self.department_filter.clear()
        self.department_filter.addItem("Все отделы")
        
        if not self.employees_df.empty:
            departments = sorted(self.employees_df['department_name'].unique())
            self.department_filter.addItems(departments)
        
        # Восстанавливаем выбранный пункт
        index = self.department_filter.findText(current_text)
        if index >= 0:
            self.department_filter.setCurrentIndex(index)
    
    def populate_employees_table(self):
        """Заполнение таблицы данными"""
        self.employees_table.setRowCount(0)
        
        if self.employees_df.empty:
            return
        
        # Применяем фильтры
        filtered_df = self.apply_filters()
        
        # Заполняем строки
        for i, row in filtered_df.iterrows():
            self.employees_table.insertRow(i)
            
            # ID (скрытый)
            id_item = QTableWidgetItem(str(row['employee_id']))
            self.employees_table.setItem(i, 0, id_item)
            
            # ФИО
            name_item = QTableWidgetItem(row['full_name'])
            name_item.setForeground(QBrush(QColor(0, 0, 0)))  # Черный текст
            self.employees_table.setItem(i, 1, name_item)
            
            # Отдел
            dept_item = QTableWidgetItem(row['department_name'])
            dept_item.setForeground(QBrush(QColor(0, 0, 0)))
            self.employees_table.setItem(i, 2, dept_item)
            
            # Должность
            pos_item = QTableWidgetItem(row['position'])
            pos_item.setForeground(QBrush(QColor(0, 0, 0)))
            self.employees_table.setItem(i, 3, pos_item)
            
            # Дата приема
            hire_date = pd.to_datetime(row['hire_date']).strftime('%d.%m.%Y')
            date_item = QTableWidgetItem(hire_date)
            date_item.setForeground(QBrush(QColor(0, 0, 0)))
            self.employees_table.setItem(i, 4, date_item)
            
            # Оклад
            salary_item = QTableWidgetItem(f"{row['salary']:,.0f} ₽")
            salary_item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            salary_item.setForeground(QBrush(QColor(0, 0, 0)))
            self.employees_table.setItem(i, 5, salary_item)
            
            # Стаж
            hire = pd.to_datetime(row['hire_date'])
            today = datetime.now()
            months = (today.year - hire.year) * 12 + today.month - hire.month
            exp_item = QTableWidgetItem(f"{months} мес")
            exp_item.setForeground(QBrush(QColor(0, 0, 0)))
            self.employees_table.setItem(i, 6, exp_item)
    
    def apply_filters(self):
        """Применение фильтров к данным"""
        filtered = self.employees_df.copy()
        
        # Фильтр по отделу
        dept_filter = self.department_filter.currentText()
        if dept_filter != "Все отделы":
            filtered = filtered[filtered['department_name'] == dept_filter]
        
        # Фильтр по поиску
        search_text = self.search_input.text().lower()
        if search_text:
            filtered = filtered[filtered['full_name'].str.lower().str.contains(search_text)]
        
        return filtered
    
    def filter_employees(self):
        """Фильтрация сотрудников"""
        self.populate_employees_table()
    
    def on_employee_selected(self):
        """Обработка выбора сотрудника в таблице"""
        selected_rows = self.employees_table.selectedIndexes()
        if selected_rows:
            row = selected_rows[0].row()
            employee_id = int(self.employees_table.item(row, 0).text())
            
            # Получаем данные сотрудника
            emp_data = self.db.get_employee_by_id(employee_id)
            if emp_data:
                self.current_employee = Employee.from_dict(emp_data)
                self.edit_btn.setEnabled(True)
                self.delete_btn.setEnabled(True)
    
    def add_employee(self):
        """Добавление нового сотрудника"""
        dialog = EmployeeDialog(self.db)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.refresh_data()
            QMessageBox.information(self, "Успех", "Сотрудник успешно добавлен!")
    
    def edit_employee(self):
        """Редактирование сотрудника"""
        if self.current_employee:
            dialog = EmployeeDialog(self.db, self.current_employee)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.refresh_data()
                QMessageBox.information(self, "Успех", "Данные сотрудника обновлены!")
    
    def delete_employee(self):
        """Удаление сотрудника"""
        if self.current_employee:
            reply = QMessageBox.question(
                self, 
                "Подтверждение",
                f"Вы уверены, что хотите удалить сотрудника {self.current_employee.full_name}?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.db.delete_employee(self.current_employee.employee_id)
                self.refresh_data()
                QMessageBox.information(self, "Успех", "Сотрудник удален!")
    
    def show_experience_classification(self):
        """Показать классификацию по стажу"""
        if self.employees_df.empty:
            self.analytics_text.setText("Нет данных для анализа")
            return
        
        result = self.analyzer.classify_by_experience()
        
        # Формируем отчет
        text = "📊 КЛАССИФИКАЦИЯ СОТРУДНИКОВ ПО СТАЖУ\n"
        text += "=" * 50 + "\n\n"
        
        # Подсчеты
        total = len(result)
        experienced = len(result[result['experience_category'] == 'Опытный'])
        new = len(result[result['experience_category'] == 'Новый'])
        
        text += f"Всего сотрудников: {total}\n"
        text += f"Опытные (стаж >= 12 мес): {experienced} ({experienced/total*100:.1f}%)\n"
        text += f"Новые (стаж < 12 мес): {new} ({new/total*100:.1f}%)\n\n"
        
        text += "📋 СПИСОК НОВЫХ СОТРУДНИКОВ:\n"
        new_employees = result[result['experience_category'] == 'Новый']
        for _, emp in new_employees.iterrows():
            text += f"• {emp['full_name']} - {emp['department_name']} - {emp['experience_months']:.0f} мес.\n"
        
        self.analytics_text.setText(text)
        self.tabs.setCurrentIndex(1)  # Переключаем на вкладку аналитики
    
    def show_turnover_analysis(self):
        """Показать анализ текучести"""
        if self.employees_df.empty:
            self.analytics_text.setText("Нет данных для анализа")
            return
        
        stats = self.analyzer.get_turnover_statistics()
        
        text = "⚠️ АНАЛИЗ РИСКА ТЕКУЧЕСТИ КАДРОВ\n"
        text += "=" * 50 + "\n\n"
        
        text += f"Всего сотрудников: {stats['total_employees']}\n"
        text += f"В зоне риска (стаж < 12 мес): {stats['at_risk_count']} ({stats['risk_percentage']}%)\n\n"
        
        text += "📊 РАСПРЕДЕЛЕНИЕ ПО КАТЕГОРИЯМ РИСКА:\n"
        for category, count in stats['risk_categories'].items():
            text += f"• {category}: {count}\n"
        
        if stats['risk_by_department']:
            text += "\n🏢 ПО ОТДЕЛАМ:\n"
            for dept, count in stats['risk_by_department'].items():
                text += f"• {dept}: {count}\n"
        
        self.analytics_text.setText(text)
        self.tabs.setCurrentIndex(1)
    
    def show_salary_statistics(self):
        """Показать статистику зарплат"""
        if self.employees_df.empty:
            self.analytics_text.setText("Нет данных для анализа")
            return
        
        stats = self.analyzer.get_salary_statistics()
        
        text = "💰 СТАТИСТИКА ЗАРПЛАТ\n"
        text += "=" * 50 + "\n\n"
        
        text += f"Общий фонд оплаты: {stats['total_fund']:,.0f} ₽\n"
        text += f"Средняя зарплата: {stats['average_salary']:,.0f} ₽\n"
        text += f"Медианная зарплата: {stats['median_salary']:,.0f} ₽\n"
        text += f"Минимальная зарплата: {stats['min_salary']:,.0f} ₽\n"
        text += f"Максимальная зарплата: {stats['max_salary']:,.0f} ₽\n"
        text += f"Стандартное отклонение: {stats['salary_std']:,.0f} ₽\n"
        
        self.analytics_text.setText(text)
        self.tabs.setCurrentIndex(1)
    
    def show_department_statistics(self):
        """Показать статистику по отделам"""
        if self.employees_df.empty:
            self.analytics_text.setText("Нет данных для анализа")
            return
        
        dept_stats = self.analyzer.get_department_statistics()
        
        text = "🏢 СТАТИСТИКА ПО ОТДЕЛАМ\n"
        text += "=" * 50 + "\n\n"
        
        for dept in dept_stats:
            text += f"Отдел: {dept['department_name']}\n"
            text += f"  • Сотрудников: {dept['count']}\n"
            text += f"  • Средняя зарплата: {dept['avg_salary']:,.0f} ₽\n"
            text += f"  • Мин/Макс: {dept['min_salary']:,.0f} - {dept['max_salary']:,.0f} ₽\n"
            text += f"  • Фонд отдела: {dept['total_salary']:,.0f} ₽\n\n"
        
        self.analytics_text.setText(text)
        self.tabs.setCurrentIndex(1)
    
    def plot_salary_distribution(self):
        """Построение графика зарплат"""
        if self.employees_df.empty:
            QMessageBox.warning(self, "Нет данных", "Нет данных для построения графика")
            return
        
        self.plotter.set_data(self.employees_df)
        self.plotter.plot_salary_distribution(top_n=15)
        self.tabs.setCurrentIndex(2)
    
    def plot_department_structure(self):
        """Построение структуры по отделам"""
        if self.employees_df.empty:
            QMessageBox.warning(self, "Нет данных", "Нет данных для построения графика")
            return
        
        self.plotter.set_data(self.employees_df)
        self.plotter.plot_structure_by_department()
        self.tabs.setCurrentIndex(2)
    
    def plot_turnover_risk(self):
        """Построение графика риска текучести"""
        if self.employees_df.empty:
            QMessageBox.warning(self, "Нет данных", "Нет данных для построения графика")
            return
        
        self.plotter.set_data(self.employees_df)
        self.plotter.plot_turnover_risk()
        self.tabs.setCurrentIndex(2)
    
    def plot_turnover_trend(self):
        """Построение графика динамики приема"""
        if self.employees_df.empty:
            QMessageBox.warning(self, "Нет данных", "Нет данных для построения графика")
            return
        
        self.plotter.set_data(self.employees_df)
        self.plotter.plot_turnover_trend()
        self.tabs.setCurrentIndex(2)
    
    def closeEvent(self, event):
        """Обработка закрытия окна"""
        self.db.close()
        event.accept()


class EmployeeDialog(QDialog):
    """Диалог добавления/редактирования сотрудника"""
    
    def __init__(self, db, employee=None):
        super().__init__()
        
        self.db = db
        self.employee = employee
        
        self.setWindowTitle("Добавление сотрудника" if not employee else "Редактирование сотрудника")
        self.setModal(True)
        self.setMinimumWidth(400)
        
        # Стиль для диалога
        self.setStyleSheet("""
            QDialog {
                background-color: #f0f0f0;
            }
            QLabel {
                color: #000000;
            }
            QLineEdit {
                border: 1px solid #000000;
                padding: 5px;
                border-radius: 3px;
                background-color: white;
                color: #000000;
            }
            QComboBox {
                border: 1px solid #000000;
                padding: 5px;
                border-radius: 3px;
                background-color: white;
                color: #000000;
            }
            QDateEdit {
                border: 1px solid #000000;
                padding: 5px;
                border-radius: 3px;
                background-color: white;
                color: #000000;
            }
            QPushButton {
                background-color: #ffffff;
                color: #000000;
                border: 2px solid #000000;
                padding: 8px 15px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        
        self.setup_ui()
        
        if employee:
            self.load_employee_data()
    
    def setup_ui(self):
        """Создание интерфейса диалога"""
        layout = QVBoxLayout(self)
        
        # Поля ввода
        form_layout = QFormLayout()
        
        self.full_name_edit = QLineEdit()
        self.full_name_edit.setPlaceholderText("Иванов Иван Иванович")
        form_layout.addRow("ФИО:", self.full_name_edit)
        
        # Выбор отдела
        self.department_combo = QComboBox()
        departments = self.db.get_departments()
        for dept in departments:
            self.department_combo.addItem(dept['name'], dept['id'])
        form_layout.addRow("Отдел:", self.department_combo)
        
        self.position_edit = QLineEdit()
        self.position_edit.setPlaceholderText("Должность")
        form_layout.addRow("Должность:", self.position_edit)
        
        self.hire_date_edit = QDateEdit()
        self.hire_date_edit.setDate(QDate.currentDate())
        self.hire_date_edit.setCalendarPopup(True)
        self.hire_date_edit.setDisplayFormat("yyyy-MM-dd")
        form_layout.addRow("Дата приема:", self.hire_date_edit)
        
        self.salary_edit = QLineEdit()
        self.salary_edit.setPlaceholderText("0.00")
        self.salary_edit.setValidator(QDoubleValidator(0, 1000000, 2))
        form_layout.addRow("Оклад:", self.salary_edit)
        
        layout.addLayout(form_layout)
        
        # Кнопки
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        # Стиль для кнопок в button box
        for button in button_box.buttons():
            button.setStyleSheet("""
                QPushButton {
                    background-color: #ffffff;
                    color: #000000;
                    border: 2px solid #000000;
                    padding: 8px 15px;
                    border-radius: 4px;
                    font-weight: bold;
                    min-width: 80px;
                }
                QPushButton:hover {
                    background-color: #e0e0e0;
                }
            """)
        
        layout.addWidget(button_box)
    
    def load_employee_data(self):
        """Загрузка данных сотрудника для редактирования"""
        self.full_name_edit.setText(self.employee.full_name)
        
        # Выбор отдела
        index = self.department_combo.findData(self.employee.department_id)
        if index >= 0:
            self.department_combo.setCurrentIndex(index)
        
        self.position_edit.setText(self.employee.position)
        
        # Дата приема
        hire_date = QDate.fromString(self.employee.hire_date, "yyyy-MM-dd")
        self.hire_date_edit.setDate(hire_date)
        
        self.salary_edit.setText(str(self.employee.salary))
    
    def accept(self):
        """Сохранение данных"""
        # Валидация
        if not self.full_name_edit.text():
            QMessageBox.warning(self, "Ошибка", "Введите ФИО сотрудника")
            return
        
        if not self.position_edit.text():
            QMessageBox.warning(self, "Ошибка", "Введите должность")
            return
        
        if not self.salary_edit.text():
            QMessageBox.warning(self, "Ошибка", "Введите оклад")
            return
        
        try:
            salary = float(self.salary_edit.text())
            if salary <= 0:
                QMessageBox.warning(self, "Ошибка", "Оклад должен быть положительным числом")
                return
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Некорректное значение оклада")
            return
        
        # Получение данных
        full_name = self.full_name_edit.text()
        department_id = self.department_combo.currentData()
        position = self.position_edit.text()
        hire_date = self.hire_date_edit.date().toString("yyyy-MM-dd")
        
        if self.employee:
            # Обновление
            self.db.update_employee(
                self.employee.employee_id,
                full_name,
                department_id,
                position,
                hire_date,
                salary
            )
        else:
            # Добавление
            self.db.add_employee(full_name, department_id, position, hire_date, salary)
        
        super().accept()

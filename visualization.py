import matplotlib
matplotlib.use('Qt5Agg')  # Важно! Указываем бэкенд для PyQt

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt6.QtWidgets import QSizePolicy, QWidget
from PyQt6.QtCore import Qt
import numpy as np

class Plotter(FigureCanvas):
    """
    Класс для визуализации данных
    Соответствует описанию в диаграмме классов
    Адаптирован для работы с PyQt6
    """
    
    def __init__(self, parent=None, width=8, height=5, dpi=100):
        """
        Инициализация холста для графиков
        
        Параметры:
        parent: родительский виджет PyQt6
        width, height: размеры фигуры в дюймах
        dpi: разрешение
        """
        # Создаем фигуру
        self.figure = Figure(figsize=(width, height), dpi=dpi)
        super().__init__(self.figure)
        
        # Устанавливаем родителя
        self.setParent(parent)
        
        # Настройка размеров
        self.setSizePolicy(QSizePolicy.Policy.Expanding, 
                          QSizePolicy.Policy.Expanding)
        self.updateGeometry()
        
        # Данные для визуализации
        self.data = None
        
        # Настройка стиля seaborn
        sns.set_style("whitegrid")
        
        # Настройка русских шрифтов
        plt.rcParams['font.family'] = 'DejaVu Sans'
        plt.rcParams['axes.unicode_minus'] = False
        
    def set_data(self, data):
        """Установка данных для визуализации"""
        self.data = data.copy() if data is not None else None
    
    def clear(self):
        """Очистка фигуры"""
        self.figure.clear()
        self.draw()
    
    def plot_salary_distribution(self, top_n=15):
        """
        Построение графика распределения зарплат
        
        Параметры:
        top_n (int): количество отображаемых сотрудников
        """
        if self.data is None or self.data.empty:
            return
        
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        # Сортировка и выбор топ-N сотрудников
        plot_data = self.data.sort_values('salary', ascending=False).head(top_n)
        
        # Построение столбчатой диаграммы
        x = range(len(plot_data))
        bars = ax.bar(x, plot_data['salary'].values, 
                     color='#3498db', edgecolor='#2c3e50', linewidth=1.5, alpha=0.8)
        
        # Настройка подписей
        ax.set_title(f'Топ-{top_n} сотрудников по зарплате', fontsize=14, pad=15, fontweight='bold')
        ax.set_xlabel('Сотрудники', fontsize=11)
        ax.set_ylabel('Зарплата (руб)', fontsize=11)
        
        # Поворот подписей
        ax.set_xticks(x)
        
        # Используем full_name если есть
        if 'full_name' in plot_data.columns:
            labels = [name.split()[0] + ' ' + name.split()[1][0] + '.' if len(name.split()) > 1 else name 
                     for name in plot_data['full_name'].tolist()]
        else:
            labels = [f'Сотр.{i+1}' for i in range(len(plot_data))]
        
        ax.set_xticklabels(labels, rotation=45, ha='right', fontsize=9)
        
        # Добавление значений на столбцы
        for i, bar in enumerate(bars):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(height):,} ₽', ha='center', va='bottom', fontsize=8, fontweight='bold')
        
        ax.grid(axis='y', linestyle='--', alpha=0.3)
        ax.set_axisbelow(True)
        
        # Добавляем горизонтальную линию средней зарплаты
        mean_salary = self.data['salary'].mean()
        ax.axhline(y=mean_salary, color='red', linestyle='--', alpha=0.7, 
                  label=f'Средняя: {int(mean_salary):,} ₽')
        ax.legend(fontsize=9)
        
        self.figure.tight_layout()
        self.draw()
    
    def plot_structure_by_department(self):
        """
        Построение круговой диаграммы структуры персонала по отделам
        """
        if self.data is None or self.data.empty:
            return
        
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        # Определяем название столбца с отделами
        dept_col = 'department_name' if 'department_name' in self.data.columns else 'department'
        
        # Подсчет сотрудников по отделам
        dept_counts = self.data[dept_col].value_counts()
        
        # Цвета для круговой диаграммы
        colors = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c']
        
        # Построение круговой диаграммы
        wedges, texts, autotexts = ax.pie(
            dept_counts.values, 
            labels=dept_counts.index,
            autopct='%1.1f%%',
            colors=colors[:len(dept_counts)],
            startangle=90,
            explode=[0.03] * len(dept_counts),
            textprops={'fontsize': 10}
        )
        
        # Настройка текста
        for text in texts:
            text.set_fontsize(10)
            text.set_fontweight('bold')
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(9)
        
        ax.set_title('Структура персонала по отделам', fontsize=14, pad=15, fontweight='bold')
        ax.axis('equal')
        
        # Добавление легенды
        ax.legend(dept_counts.index, loc='upper left', bbox_to_anchor=(1, 1), fontsize=9)
        
        self.figure.tight_layout()
        self.draw()
    
    def plot_turnover_risk(self):
        """
        Построение графика риска текучести по отделам
        """
        if self.data is None or self.data.empty:
            return
        
        self.figure.clear()
        
        # Создаем два подграфика
        ax1 = self.figure.add_subplot(121)
        ax2 = self.figure.add_subplot(122)
        
        # Анализ текучести
        temp_data = self.data.copy()
        temp_data['hire_date'] = pd.to_datetime(temp_data['hire_date'])
        today = pd.to_datetime('2024-03-01')
        temp_data['months_employed'] = ((today - temp_data['hire_date']) / np.timedelta64(1, 'D') / 30).astype(int)
        temp_data['turnover_risk'] = temp_data['months_employed'] < 6
        
        # График 1: Общий риск текучести
        risk_counts = temp_data['turnover_risk'].value_counts()
        risk_labels = ['В зоне риска', 'Стабильные']
        risk_values = [risk_counts.get(True, 0), risk_counts.get(False, 0)]
        colors = ['#e74c3c', '#2ecc71']
        
        wedges, texts, autotexts = ax1.pie(
            risk_values, 
            labels=risk_labels,
            autopct='%1.1f%%',
            colors=colors,
            startangle=90,
            explode=[0.05, 0],
            textprops={'fontsize': 10}
        )
        
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        ax1.set_title('Общий риск текучести', fontsize=12, fontweight='bold')
        ax1.axis('equal')
        
        # График 2: Риск по отделам
        dept_col = 'department_name' if 'department_name' in temp_data.columns else 'department'
        
        if risk_counts.get(True, 0) > 0:
            risk_by_dept = temp_data[temp_data['turnover_risk'] == True]
            if not risk_by_dept.empty:
                dept_risk = risk_by_dept[dept_col].value_counts()
                
                x = range(len(dept_risk))
                bars = ax2.bar(x, dept_risk.values, 
                              color='#e74c3c', edgecolor='#c0392b', linewidth=1.5, alpha=0.8)
                
                ax2.set_title('Сотрудники в зоне риска по отделам', fontsize=12, fontweight='bold')
                ax2.set_xlabel('Отдел', fontsize=10)
                ax2.set_ylabel('Количество', fontsize=10)
                ax2.set_xticks(x)
                ax2.set_xticklabels(dept_risk.index, rotation=45, ha='right', fontsize=9)
                ax2.grid(axis='y', linestyle='--', alpha=0.3)
                ax2.set_axisbelow(True)
                
                # Добавление значений
                for i, bar in enumerate(bars):
                    height = bar.get_height()
                    ax2.text(bar.get_x() + bar.get_width()/2., height,
                            int(height), ha='center', va='bottom', fontweight='bold', fontsize=10)
        else:
            ax2.text(0.5, 0.5, 'Нет сотрудников в зоне риска',
                    ha='center', va='center', transform=ax2.transAxes,
                    fontsize=12, color='green', fontweight='bold')
            ax2.set_title('Риск текучести по отделам', fontsize=12, fontweight='bold')
            ax2.axis('off')
        
        self.figure.tight_layout()
        self.draw()
    
    def plot_turnover_trend(self):
        """
        Построение графика динамики приема сотрудников
        """
        if self.data is None or self.data.empty:
            return
        
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        # Преобразование дат
        plot_data = self.data.copy()
        plot_data['hire_date'] = pd.to_datetime(plot_data['hire_date'])
        plot_data['hire_month'] = plot_data['hire_date'].dt.to_period('M')
        
        # Подсчет количества принятых по месяцам
        monthly_hires = plot_data.groupby('hire_month').size()
        
        # Сортируем по дате
        monthly_hires = monthly_hires.sort_index()
        
        # Построение линейного графика
        months = [str(m) for m in monthly_hires.index]
        values = monthly_hires.values
        
        ax.plot(range(len(months)), values, marker='o', linestyle='-', 
                color='#3498db', linewidth=2.5, markersize=8, markerfacecolor='white', 
                markeredgecolor='#2980b9', markeredgewidth=2)
        
        # Добавление заполнения
        ax.fill_between(range(len(months)), values, alpha=0.2, color='#3498db')
        
        ax.set_xlabel('Месяц приема', fontsize=11)
        ax.set_ylabel('Количество сотрудников', fontsize=11)
        ax.set_title('Динамика приема сотрудников', fontsize=14, pad=15, fontweight='bold')
        ax.grid(True, linestyle='--', alpha=0.3)
        ax.set_axisbelow(True)
        
        # Настройка подписей оси X
        ax.set_xticks(range(len(months)))
        ax.set_xticklabels(months, rotation=45, ha='right', fontsize=9)
        
        # Добавление значений на график
        for i, (month, count) in enumerate(zip(months, values)):
            ax.annotate(str(count), (i, count), textcoords="offset points", 
                       xytext=(0, 10), ha='center', fontsize=9, fontweight='bold')
        
        self.figure.tight_layout()
        self.draw()
    
    def plot_salary_by_department(self):
        """
        Построение графика распределения зарплат по отделам
        """
        if self.data is None or self.data.empty:
            return
        
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        # Определяем название столбца с отделами
        dept_col = 'department_name' if 'department_name' in self.data.columns else 'department'
        
        # Подготовка данных
        dept_salary = self.data.groupby(dept_col)['salary'].agg(['mean', 'min', 'max']).reset_index()
        dept_salary.columns = [dept_col, 'mean', 'min', 'max']
        
        # Сортируем по средней зарплате
        dept_salary = dept_salary.sort_values('mean', ascending=True)
        
        # Построение горизонтальной столбчатой диаграммы
        y = range(len(dept_salary))
        
        # Создаем три набора баров
        bar_height = 0.25
        y1 = [i - bar_height for i in y]
        y2 = y
        y3 = [i + bar_height for i in y]
        
        bars1 = ax.barh(y1, dept_salary['min'].values, bar_height, 
                        label='Минимум', color='#95a5a6', edgecolor='#7f8c8d', alpha=0.8)
        bars2 = ax.barh(y2, dept_salary['mean'].values, bar_height, 
                        label='Среднее', color='#3498db', edgecolor='#2980b9', alpha=0.8)
        bars3 = ax.barh(y3, dept_salary['max'].values, bar_height, 
                        label='Максимум', color='#2ecc71', edgecolor='#27ae60', alpha=0.8)
        
        ax.set_xlabel('Зарплата (руб)', fontsize=11)
        ax.set_ylabel('Отдел', fontsize=11)
        ax.set_title('Анализ зарплат по отделам', fontsize=14, pad=15, fontweight='bold')
        ax.set_yticks(y)
        ax.set_yticklabels(dept_salary[dept_col].tolist(), fontsize=10)
        ax.legend(loc='lower right', fontsize=9)
        ax.grid(axis='x', linestyle='--', alpha=0.3)
        ax.set_axisbelow(True)
        
        # Добавление значений
        for bars, values in [(bars1, dept_salary['min'].values), 
                            (bars2, dept_salary['mean'].values), 
                            (bars3, dept_salary['max'].values)]:
            for i, (bar, val) in enumerate(zip(bars, values)):
                ax.text(val + 500, bar.get_y() + bar.get_height()/2,
                       f'{int(val/1000)}K', ha='left', va='center', fontsize=8, fontweight='bold')
        
        self.figure.tight_layout()
        self.draw()
    
    def plot_experience_classification(self):
        """
        Построение графика классификации по стажу
        """
        if self.data is None or self.data.empty:
            return
        
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        # Расчет стажа
        temp_data = self.data.copy()
        temp_data['hire_date'] = pd.to_datetime(temp_data['hire_date'])
        today = pd.to_datetime('2024-03-01')
        temp_data['months_employed'] = ((today - temp_data['hire_date']) / np.timedelta64(1, 'D') / 30).astype(int)
        
        # Классификация
        def exp_cat(months):
            if months < 3:
                return 'Новые (до 3 мес)'
            elif months < 12:
                return 'Средний стаж (3-12 мес)'
            else:
                return 'Опытные (более года)'
        
        temp_data['exp_category'] = temp_data['months_employed'].apply(exp_cat)
        
        # Подсчет
        cat_counts = temp_data['exp_category'].value_counts()
        
        # Порядок категорий
        order = ['Новые (до 3 мес)', 'Средний стаж (3-12 мес)', 'Опытные (более года)']
        cat_counts = cat_counts.reindex(order, fill_value=0)
        
        # Цвета
        colors = ['#e74c3c', '#f39c12', '#2ecc71']
        
        # Построение
        x = range(len(cat_counts))
        bars = ax.bar(x, cat_counts.values, color=colors, edgecolor='black', linewidth=1.5, alpha=0.8)
        
        ax.set_xlabel('Категория', fontsize=11)
        ax.set_ylabel('Количество сотрудников', fontsize=11)
        ax.set_title('Классификация сотрудников по стажу', fontsize=14, pad=15, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(cat_counts.index, rotation=15, ha='right', fontsize=9)
        ax.grid(axis='y', linestyle='--', alpha=0.3)
        ax.set_axisbelow(True)
        
        # Добавление значений
        for i, (bar, count) in enumerate(zip(bars, cat_counts.values)):
            ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.1,
                   str(count), ha='center', va='bottom', fontweight='bold', fontsize=11)
        
        self.figure.tight_layout()
        self.draw()

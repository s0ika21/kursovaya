import pandas as pd
from datetime import datetime
from models import Employee

class DataAnalyzer:
    """
    Класс для анализа кадровых данных
    Соответствует описанию в диаграмме классов
    """
    
    def __init__(self, employees_df=None):
        """
        Инициализация анализатора
        
        Параметры:
        employees_df (pd.DataFrame): DataFrame с данными сотрудников
        """
        self.employees = employees_df if employees_df is not None else pd.DataFrame()
    
    def set_data(self, employees_df):
        """Установка данных для анализа"""
        self.employees = employees_df.copy()
    
    def classify_by_experience(self, threshold_months=12):
        """
        Классификация сотрудников по стажу работы
        
        Параметры:
        threshold_months (int): пороговое значение стажа в месяцах
        
        Возвращает:
        pd.DataFrame: данные с добавленными колонками классификации
        
        Реализация алгоритма из раздела 2.4
        """
        if self.employees.empty:
            return self.employees
        
        result = self.employees.copy()
        
        # Проверка наличия необходимого столбца
        if 'hire_date' not in result.columns:
            raise ValueError("Отсутствует столбец 'hire_date' в данных")
        
        # Преобразование даты приема
        result['hire_date'] = pd.to_datetime(result['hire_date'])
        
        # Расчет стажа в месяцах
        current_date = datetime.now()
        result['experience_days'] = (current_date - result['hire_date']).dt.days
        result['experience_months'] = (result['experience_days'] / 30.44).round(1)
        
        # Классификация по стажу
        result['experience_category'] = result['experience_months'].apply(
            lambda months: 'Опытный' if months >= threshold_months else 'Новый'
        )
        
        # Удаляем промежуточный столбец
        result = result.drop('experience_days', axis=1)
        
        return result
    
    def analyze_turnover_risk(self, risk_period_months=12):
        """
        Анализ риска текучести кадров
        
        Параметры:
        risk_period_months (int): период в месяцах, считающийся зоной риска
        
        Возвращает:
        pd.DataFrame: данные с колонками анализа текучести
        
        Реализация алгоритма из раздела 2.4
        """
        if self.employees.empty:
            return self.employees
        
        result = self.employees.copy()
        
        # Проверка наличия необходимого столбца
        if 'hire_date' not in result.columns:
            raise ValueError("Отсутствует столбец 'hire_date' в данных")
        
        # Преобразование даты приема
        result['hire_date'] = pd.to_datetime(result['hire_date'])
        
        # Расчет стажа
        current_date = datetime.now()
        result['employment_days'] = (current_date - result['hire_date']).dt.days
        result['employment_months'] = (result['employment_days'] / 30.44).round(1)
        
        # Определение риска текучести
        result['turnover_risk'] = result['employment_months'] < risk_period_months
        
        # Категоризация риска
        def categorize_risk(months):
            if months < 3:
                return 'Высокий'  # Испытательный срок
            elif months < 6:
                return 'Средний'   # Первые полгода
            elif months < 12:
                return 'Низкий'    # Меньше года, но уже адаптировался
            else:
                return 'Отсутствует'  # Стабильные сотрудники
        
        result['risk_category'] = result['employment_months'].apply(categorize_risk)
        
        # Удаление промежуточного столбца
        result = result.drop('employment_days', axis=1)
        
        return result
    
    def get_department_statistics(self):
        """
        Получение статистики по отделам
        
        Возвращает:
        dict: статистика по отделам
        """
        if self.employees.empty:
            return {}
        
        # Группировка по отделам
        dept_stats = self.employees.groupby('department_name').agg({
            'employee_id': 'count',
            'salary': ['mean', 'min', 'max', 'sum']
        }).round(2)
        
        dept_stats.columns = ['count', 'avg_salary', 'min_salary', 'max_salary', 'total_salary']
        dept_stats = dept_stats.reset_index()
        
        return dept_stats.to_dict('records')
    
    def get_turnover_statistics(self):
        """
        Формирование статистики по текучести
        
        Возвращает:
        dict: словарь со статистикой текучести
        """
        if self.employees.empty:
            return {}
        
        # Применяем анализ текучести
        turnover_data = self.analyze_turnover_risk()
        
        stats = {}
        stats['total_employees'] = len(turnover_data)
        stats['at_risk_count'] = turnover_data['turnover_risk'].sum()
        stats['risk_percentage'] = round(
            (stats['at_risk_count'] / stats['total_employees'] * 100), 1
        )
        
        # Распределение по категориям риска
        stats['risk_categories'] = turnover_data['risk_category'].value_counts().to_dict()
        
        # Статистика по отделам
        dept_risk = turnover_data[turnover_data['turnover_risk'] == True].groupby('department_name').size()
        stats['risk_by_department'] = dept_risk.to_dict()
        
        return stats
    
    def get_salary_statistics(self):
        """
        Получение статистики по зарплатам
        
        Возвращает:
        dict: статистика по зарплатам
        """
        if self.employees.empty:
            return {}
        
        stats = {
            'total_fund': self.employees['salary'].sum(),
            'average_salary': round(self.employees['salary'].mean(), 2),
            'median_salary': round(self.employees['salary'].median(), 2),
            'min_salary': self.employees['salary'].min(),
            'max_salary': self.employees['salary'].max(),
            'salary_std': round(self.employees['salary'].std(), 2)
        }
        
        return stats
    
    def generate_department_report(self, department_name):
        """
        Формирование отчета по конкретному отделу
        
        Параметры:
        department_name (str): название отдела
        
        Возвращает:
        dict: отчет по отделу
        """
        if self.employees.empty:
            return {}
        
        dept_data = self.employees[self.employees['department_name'] == department_name]
        
        if dept_data.empty:
            return {}
        
        report = {
            'department': department_name,
            'employee_count': len(dept_data),
            'total_salary': dept_data['salary'].sum(),
            'avg_salary': round(dept_data['salary'].mean(), 2),
            'positions': dept_data['position'].tolist()
        }
        
        # Анализ текучести по отделу
        turnover_data = self.analyze_turnover_risk()
        dept_turnover = turnover_data[turnover_data['department_name'] == department_name]
        report['at_risk_count'] = dept_turnover['turnover_risk'].sum()
        
        return report

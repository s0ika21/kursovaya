from dataclasses import dataclass
from datetime import datetime

@dataclass
class Employee:
    """
    Класс для представления информации о сотруднике
    Соответствует описанию в твоей диаграмме классов
    """
    employee_id: int = None
    full_name: str = ""
    department_id: int = None
    department_name: str = ""
    position: str = ""
    hire_date: str = ""
    salary: float = 0.0
    
    def get_employment_duration(self) -> int:
        """
        Вычисление стажа работы в месяцах
        Метод из диаграммы классов
        """
        if not self.hire_date:
            return 0
        
        hire = datetime.strptime(self.hire_date, "%Y-%m-%d")
        today = datetime.now()
        
        # Разница в днях, переводим в месяцы
        days = (today - hire).days
        months = days // 30
        return months
    
    def calculate_salary(self) -> float:
        """
        Расчет заработной платы (в текущей версии просто возвращает оклад)
        Метод из диаграммы классов
        """
        # Здесь может быть логика расчета с учетом налогов, премий и т.д.
        return self.salary
    
    def to_dict(self):
        """Преобразование в словарь для БД"""
        return {
            'employee_id': self.employee_id,
            'full_name': self.full_name,
            'department_id': self.department_id,
            'position': self.position,
            'hire_date': self.hire_date,
            'salary': self.salary
        }
    
    @classmethod
    def from_dict(cls, data):
        """Создание объекта из словаря"""
        return cls(
            employee_id=data.get('employee_id'),
            full_name=data.get('full_name', ''),
            department_id=data.get('department_id'),
            department_name=data.get('department_name', ''),
            position=data.get('position', ''),
            hire_date=data.get('hire_date', ''),
            salary=data.get('salary', 0.0)
        )

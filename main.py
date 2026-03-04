#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Главный файл запуска приложения "Учет персонала"
Разработан в соответствии с курсовой работой
"""

import sys
from PyQt6.QtWidgets import QApplication
from gui import HRApp

def main():
    """Точка входа в приложение"""
    
    # Создание приложения
    app = QApplication(sys.argv)
    app.setApplicationName("Учет персонала")
    app.setOrganizationName("HR Department")
    
    # Установка стиля
    app.setStyle('Fusion')
    
    # Создание и отображение главного окна
    window = HRApp()
    window.show()
    
    # Запуск цикла обработки событий
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

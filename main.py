# main.py

import sys
from PyQt6.QtWidgets import QApplication
from windows import RegistrationWindow  # Импортируем класс окна из пакета 'windows'
from config import APP_NAME


def main():
    # 1. Создаем объект приложения
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)

    # 2. Создаем и показываем первое окно
    # Это будет либо RegistrationWindow, либо сразу главное меню,

    main_window = RegistrationWindow()
    main_window.show()

    # 3. Запускаем основной цикл обработки событий PyQt
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
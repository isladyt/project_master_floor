# main.py

import sys
from PyQt6.QtWidgets import QApplication
from windows.registration_window import RegistrationWindow
from config import APP_NAME


def main():
    # 1. Создаем объект приложения
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)

    # 2. Создаем и показываем окно регистрации/входа
    auth_window = RegistrationWindow()
    auth_window.show()

    # 3. Запускаем основной цикл обработки событий PyQt
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

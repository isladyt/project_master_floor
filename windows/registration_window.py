# windows/registration_window.py (МИНИМАЛЬНО)

from PyQt6.QtWidgets import QMainWindow, QLabel

class RegistrationWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Регистрация/Вход")
        self.setGeometry(100, 100, 400, 300)
        # Временная заглушка
        self.label = QLabel("Окно Регистрации (UI еще нет)", self)
        self.label.move(100, 100)
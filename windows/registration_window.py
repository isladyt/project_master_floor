# windows/registration_window.py

from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QStackedWidget,
                             QMessageBox, QFrame, QGridLayout, QGroupBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from db.models import get_user_by_login, register_new_user, debug_check_users
from config import USER_ROLES
from .base_window import BaseWindow


class RegistrationWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_user = None
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("ERP System Manager - Авторизация")
        self.setFixedSize(500, 400)
        
        # Центрирование окна
        screen_geometry = self.screen().availableGeometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)
        
        # Создание центрального виджета
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Создание stacked widget для переключения между окнами
        self.stacked_widget = QStackedWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.stacked_widget)
        central_widget.setLayout(layout)
        
        # Создание окон
        self.login_widget = self.create_login_widget()
        self.register_widget = self.create_register_widget()
        
        # Добавление окон в stacked widget
        self.stacked_widget.addWidget(self.login_widget)
        self.stacked_widget.addWidget(self.register_widget)
        
        # Показ окна входа
        self.show_login()
    
    def create_login_widget(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Заголовок
        title = QLabel("Вход в систему")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Поля ввода
        input_frame = QFrame()
        input_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        input_layout = QVBoxLayout()
        input_layout.setSpacing(15)
        
        # Логин
        login_layout = QVBoxLayout()
        login_label = QLabel("Логин:")
        login_label.setFont(QFont("Arial", 10))
        self.login_input = QLineEdit()
        self.login_input.setPlaceholderText("Введите ваш логин")
        self.login_input.setMinimumHeight(35)
        login_layout.addWidget(login_label)
        login_layout.addWidget(self.login_input)
        
        # Пароль
        password_layout = QVBoxLayout()
        password_label = QLabel("Пароль:")
        password_label.setFont(QFont("Arial", 10))
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Введите ваш пароль")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setMinimumHeight(35)
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_input)
        
        input_layout.addLayout(login_layout)
        input_layout.addLayout(password_layout)
        input_frame.setLayout(input_layout)
        layout.addWidget(input_frame)
        
        # Кнопки
        button_layout = QHBoxLayout()
        
        self.login_btn = QPushButton("Войти")
        self.login_btn.setMinimumHeight(40)
        self.login_btn.setStyleSheet("""
            QPushButton {
                background-color: #2E7D32;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1B5E20;
            }
        """)
        self.login_btn.clicked.connect(self.login)
        
        self.register_btn = QPushButton("Регистрация")
        self.register_btn.setMinimumHeight(40)
        self.register_btn.setStyleSheet("""
            QPushButton {
                background-color: #1565C0;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0D47A1;
            }
        """)
        self.register_btn.clicked.connect(self.show_register)
        
        button_layout.addWidget(self.login_btn)
        button_layout.addWidget(self.register_btn)
        layout.addLayout(button_layout)
        
        widget.setLayout(layout)
        return widget
    
    def create_register_widget(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Заголовок
        title = QLabel("Регистрация партнера")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Основная форма
        form_frame = QFrame()
        form_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        form_layout = QGridLayout()
        form_layout.setSpacing(15)
        form_layout.setColumnStretch(1, 1)
        
        # Данные компании
        company_group = QGroupBox("Данные компании")
        company_layout = QGridLayout()
        company_layout.setSpacing(10)
        
        row = 0
        company_layout.addWidget(QLabel("Название компании:"), row, 0)
        self.company_name = QLineEdit()
        self.company_name.setPlaceholderText("ООО 'Пример'")
        company_layout.addWidget(self.company_name, row, 1)
        
        row += 1
        company_layout.addWidget(QLabel("ИНН:"), row, 0)
        self.inn = QLineEdit()
        self.inn.setPlaceholderText("10 цифр")
        self.inn.setMaxLength(12)
        company_layout.addWidget(self.inn, row, 1)
        
        row += 1
        company_layout.addWidget(QLabel("Директор:"), row, 0)
        self.director = QLineEdit()
        self.director.setPlaceholderText("ФИО директора")
        company_layout.addWidget(self.director, row, 1)
        
        row += 1
        company_layout.addWidget(QLabel("Email:"), row, 0)
        self.email = QLineEdit()
        self.email.setPlaceholderText("email@example.com")
        company_layout.addWidget(self.email, row, 1)
        
        company_group.setLayout(company_layout)
        form_layout.addWidget(company_group, 0, 0, 1, 2)
        
        # Данные для входа
        auth_group = QGroupBox("Данные для входа")
        auth_layout = QGridLayout()
        auth_layout.setSpacing(10)
        
        row = 0
        auth_layout.addWidget(QLabel("Логин:"), row, 0)
        self.username = QLineEdit()
        self.username.setPlaceholderText("Придумайте логин")
        auth_layout.addWidget(self.username, row, 1)
        
        row += 1
        auth_layout.addWidget(QLabel("Пароль:"), row, 0)
        self.password = QLineEdit()
        self.password.setPlaceholderText("Придумайте пароль")
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        auth_layout.addWidget(self.password, row, 1)
        
        row += 1
        auth_layout.addWidget(QLabel("Подтверждение пароля:"), row, 0)
        self.confirm_password = QLineEdit()
        self.confirm_password.setPlaceholderText("Повторите пароль")
        self.confirm_password.setEchoMode(QLineEdit.EchoMode.Password)
        auth_layout.addWidget(self.confirm_password, row, 1)
        
        auth_group.setLayout(auth_layout)
        form_layout.addWidget(auth_group, 1, 0, 1, 2)
        
        form_frame.setLayout(form_layout)
        layout.addWidget(form_frame)
        
        # Кнопки
        button_layout = QHBoxLayout()
        
        self.register_btn = QPushButton("Зарегистрироваться")
        self.register_btn.setMinimumHeight(40)
        self.register_btn.setStyleSheet("""
            QPushButton {
                background-color: #1565C0;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0D47A1;
            }
        """)
        self.register_btn.clicked.connect(self.register)
        
        self.back_btn = QPushButton("Назад")
        self.back_btn.setMinimumHeight(40)
        self.back_btn.setStyleSheet("""
            QPushButton {
                background-color: #757575;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #424242;
            }
        """)
        self.back_btn.clicked.connect(self.show_login)
        
        button_layout.addWidget(self.register_btn)
        button_layout.addWidget(self.back_btn)
        layout.addLayout(button_layout)
        
        widget.setLayout(layout)
        return widget
    
    def show_login(self):
        self.stacked_widget.setCurrentWidget(self.login_widget)
        self.setWindowTitle("ERP System Manager - Вход в систему")
        self.setFixedSize(500, 400)
    
    def show_register(self):
        self.stacked_widget.setCurrentWidget(self.register_widget)
        self.setWindowTitle("ERP System Manager - Регистрация")
        self.setFixedSize(600, 600)
    
    def login(self):
        username = self.login_input.text().strip()
        password = self.password_input.text().strip()
        
        if not username or not password:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля")
            return
        
        # ОТЛАДКА: покажем всех пользователей в БД
        print("\n" + "="*50)
        print("ОТЛАДКА АВТОРИЗАЦИИ:")
        debug_check_users()
        print(f"Попытка входа: username='{username}', password='{password}'")
        print("="*50 + "\n")
        
        user = get_user_by_login(username, password)
        
        print(f"Результат авторизации: {user}")  # ОТЛАДКА
        
        if user:
            role_name = USER_ROLES.get(user['role_id'], "Unknown")
            QMessageBox.information(self, "Успех", 
                                  f"Добро пожаловать, {user['username']}!\n"
                                  f"Роль: {role_name}")
            self.show_main_window(user)
        else:
            QMessageBox.critical(self, "Ошибка", "Неверный логин или пароль")
    
    def validate_register_input(self):
        # Проверка обязательных полей
        required_fields = {
            "Название компании": self.company_name.text().strip(),
            "ИНН": self.inn.text().strip(),
            "Директор": self.director.text().strip(),
            "Email": self.email.text().strip(),
            "Логин": self.username.text().strip(),
            "Пароль": self.password.text().strip(),
            "Подтверждение пароля": self.confirm_password.text().strip()
        }
        
        for field_name, value in required_fields.items():
            if not value:
                QMessageBox.warning(self, "Ошибка", f"Поле '{field_name}' обязательно для заполнения")
                return False
        
        # Проверка ИНН (должен содержать только цифры)
        if not self.inn.text().strip().isdigit() or len(self.inn.text().strip()) != 10:
            QMessageBox.warning(self, "Ошибка", "ИНН должен содержать 10 цифр")
            return False
        
        # Проверка email (базовая проверка)
        email = self.email.text().strip()
        if '@' not in email or '.' not in email:
            QMessageBox.warning(self, "Ошибка", "Введите корректный email адрес")
            return False
        
        # Проверка совпадения паролей
        if self.password.text() != self.confirm_password.text():
            QMessageBox.warning(self, "Ошибка", "Пароли не совпадают")
            return False
        
        # Проверка минимальной длины пароля
        if len(self.password.text()) < 6:
            QMessageBox.warning(self, "Ошибка", "Пароль должен содержать минимум 6 символов")
            return False
            
        return True
    
    def register(self):
        if not self.validate_register_input():
            return
            
        user_data = {
            'company_name': self.company_name.text().strip(),
            'inn': self.inn.text().strip(),
            'director_name': self.director.text().strip(),
            'email': self.email.text().strip(),
            'username': self.username.text().strip(),
            'password_hash': self.password.text().strip(),
            'role_id': 1
        }
        
        print(f"Пытаемся зарегистрировать пользователя: {user_data}")  # ДЛЯ ОТЛАДКИ
        
        try:
            success, message = register_new_user(user_data)
            print(f"Результат регистрации: success={success}, message={message}")  # ДЛЯ ОТЛАДКИ
            if success:
                QMessageBox.information(self, "Успех", message)
                self.clear_register_fields()
                self.show_login()
            else:
                QMessageBox.critical(self, "Ошибка", message)
        except Exception as e:
            print(f"Исключение при регистрации: {e}")  # ДЛЯ ОТЛАДКИ
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка: {str(e)}")
    
    def clear_register_fields(self):
        """Очистка полей формы регистрации"""
        self.company_name.clear()
        self.inn.clear()
        self.director.clear()
        self.email.clear()
        self.username.clear()
        self.password.clear()
        self.confirm_password.clear()
    
    def show_main_window(self, user_data):
        """Переход к главному окну (будет реализовано другими разработчиками)"""
        QMessageBox.information(self, "Успешный вход", 
                              f"Вход выполнен успешно!\n\n"
                              f"Пользователь: {user_data['username']}\n"
                              f"Роль: {USER_ROLES.get(user_data['role_id'], 'Unknown')}\n\n"
                              "Главное окно системы будет реализовано другими разработчиками.")
        
        # Здесь будет переход к главному окну, которое сделают другие разработчики
        # Например: 
        # from .main_window import MainWindow
        # self.main_window = MainWindow(user_data)
        # self.main_window.show()
        # self.hide()

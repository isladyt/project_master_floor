import sys
import pymysql
import hashlib
import random
import string
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
                             QLineEdit, QLabel, QMessageBox, QDialog, QFormLayout,
                             QHeaderView, QFrame, QComboBox, QGroupBox, QCheckBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class DatabaseManager:
    """Класс для управления подключением к базе данных MySQL"""

    def __init__(self):
        self.connection = None
        self.connect()
        if self.connection:
            self.initialize_base_data()

    def connect(self):
        """Установка подключения к базе данных"""
        try:
            self.connection = pymysql.connect(
                host='localhost',
                user='root',
                password='root',
                database='master_floor',
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )
            print("Успешное подключение к базе данных MySQL")
            return True
        except pymysql.Error as e:
            print(f"Ошибка подключения к MySQL: {e}")
            QMessageBox.critical(None, "Ошибка базы данных",
                                 f"Не удалось подключиться к базе данных:\n{str(e)}")
            return False

    def initialize_base_data(self):
        """Инициализация базовых данных при первом запуске"""
        try:
            with self.connection.cursor() as cursor:
                # Проверяем наличие типов партнеров
                cursor.execute("SELECT COUNT(*) as count FROM partner_types")
                result = cursor.fetchone()

                if result and result['count'] == 0:
                    cursor.execute("""
                        INSERT INTO partner_types (type_name) VALUES 
                        ('ООО'), ('ЗАО'), ('ПАО'), ('ИП'), ('АО')
                    """)
                    self.connection.commit()
                    print("Базовые типы партнеров добавлены")

                # Проверяем наличие ролей
                cursor.execute("SELECT COUNT(*) as count FROM roles")
                result = cursor.fetchone()

                if result and result['count'] == 0:
                    cursor.execute("""
                        INSERT INTO roles (role_name) VALUES 
                        ('Admin'), ('Partner_Admin'), ('Partner_User'), ('Manager')
                    """)
                    self.connection.commit()
                    print("Базовые роли добавлены")

        except pymysql.Error as e:
            print(f"Ошибка инициализации базовых данных: {e}")

    def get_partner_types(self):
        """Получение всех типов партнеров"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT type_id, type_name FROM partner_types ORDER BY type_name")
                return cursor.fetchall()
        except pymysql.Error as e:
            print(f"Ошибка получения типов партнеров: {e}")
            return []

    def hash_password(self, password):
        """Хеширование пароля"""
        return hashlib.sha256(password.encode()).hexdigest()

    def generate_random_password(self, length=8):
        """Генерация случайного пароля"""
        characters = string.ascii_letters + string.digits
        return ''.join(random.choice(characters) for i in range(length))

    def create_partner_user(self, partner_id, username, password=None):
        """Создание пользователя для партнера (один пользователь на партнера)"""
        try:
            with self.connection.cursor() as cursor:
                # Проверяем, существует ли уже пользователь для этого партнера
                cursor.execute("SELECT user_id, username FROM users WHERE partner_id = %s", (partner_id,))
                existing_user = cursor.fetchone()

                if existing_user:
                    return False, f"Для этого партнера уже существует пользователь: {existing_user['username']}"

                # Проверяем, существует ли пользователь с таким username
                cursor.execute("SELECT user_id FROM users WHERE username = %s", (username,))
                if cursor.fetchone():
                    return False, "Пользователь с таким логином уже существует"

                # Генерируем пароль если не указан
                if not password:
                    password = self.generate_random_password()

                # Хешируем пароль
                password_hash = self.hash_password(password)

                # Получаем role_id для роли 'Partner_User'
                cursor.execute("SELECT role_id FROM roles WHERE role_name = 'Partner_User'")
                role_result = cursor.fetchone()
                if not role_result:
                    cursor.execute("SELECT role_id FROM roles LIMIT 1")
                    role_result = cursor.fetchone()

                role_id = role_result['role_id'] if role_result else 1

                cursor.execute(
                    """INSERT INTO users (username, password_hash, role_id, partner_id)
                    VALUES (%s, %s, %s, %s)""",
                    (username, password_hash, role_id, partner_id)
                )
                self.connection.commit()
                return True, password

        except pymysql.Error as e:
            print(f"Ошибка создания пользователя партнера: {e}")
            self.connection.rollback()
            return False, f"Ошибка базы данных: {str(e)}"

    def get_partner_user(self, partner_id):
        """Получение пользователя партнера (только одного)"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT u.user_id, u.username, r.role_name, u.partner_id
                    FROM users u
                    LEFT JOIN roles r ON u.role_id = r.role_id
                    WHERE u.partner_id = %s
                """, (partner_id,))
                return cursor.fetchone()  # Возвращаем только одного пользователя
        except pymysql.Error as e:
            print(f"Ошибка получения пользователя партнера: {e}")
            return None

    def update_partner_user(self, user_id, user_data):
        """Обновление данных пользователя партнера"""
        try:
            with self.connection.cursor() as cursor:
                # Проверяем, не занят ли новый логин другим пользователем
                cursor.execute("SELECT user_id FROM users WHERE username = %s AND user_id != %s",
                               (user_data['username'], user_id))
                if cursor.fetchone():
                    return False, "Пользователь с таким логином уже существует"

                if user_data.get('password'):
                    password_hash = self.hash_password(user_data['password'])
                    cursor.execute(
                        """UPDATE users 
                        SET username = %s, password_hash = %s 
                        WHERE user_id = %s""",
                        (user_data['username'], password_hash, user_id)
                    )
                else:
                    cursor.execute(
                        """UPDATE users 
                        SET username = %s 
                        WHERE user_id = %s""",
                        (user_data['username'], user_id)
                    )

                self.connection.commit()
                return True, "Данные пользователя обновлены"

        except pymysql.Error as e:
            print(f"Ошибка обновления пользователя партнера: {e}")
            self.connection.rollback()
            return False, f"Ошибка базы данных: {str(e)}"

    def delete_partner_user(self, user_id):
        """Удаление пользователя партнера"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
                self.connection.commit()
                return True
        except pymysql.Error as e:
            print(f"Ошибка удаления пользователя партнера: {e}")
            self.connection.rollback()
            return False

    def reset_partner_user_password(self, user_id):
        """Сброс пароля пользователя партнера"""
        try:
            with self.connection.cursor() as cursor:
                new_password = self.generate_random_password()
                password_hash = self.hash_password(new_password)

                cursor.execute(
                    "UPDATE users SET password_hash = %s WHERE user_id = %s",
                    (password_hash, user_id)
                )
                self.connection.commit()
                return True, new_password
        except pymysql.Error as e:
            print(f"Ошибка сброса пароля: {e}")
            self.connection.rollback()
            return False, f"Ошибка базы данных: {str(e)}"

    def get_all_partners(self):
        """Получение всех партнеров из базы данных"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT p.*, pt.type_name as partner_type_name,
                    (SELECT COUNT(*) FROM users u WHERE u.partner_id = p.partner_id) as user_count,
                    (SELECT username FROM users u WHERE u.partner_id = p.partner_id LIMIT 1) as username
                    FROM partners p
                    LEFT JOIN partner_types pt ON p.partner_type_id = pt.type_id
                    ORDER BY p.partner_id
                """)
                return cursor.fetchall()
        except pymysql.Error as e:
            print(f"Ошибка получения партнеров: {e}")
            return []

    def add_partner(self, partner_data):
        """Добавление нового партнера в базу данных"""
        try:
            with self.connection.cursor() as cursor:
                query = """
                    INSERT INTO partners (company_name, email, contact_phone, director_name, inn, partner_type_id)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                values = (
                    partner_data['company_name'],
                    partner_data['email'],
                    partner_data['phone'],
                    partner_data['contact_person'],
                    partner_data.get('inn', ''),
                    partner_data['partner_type_id']
                )
                cursor.execute(query, values)
                partner_id = cursor.lastrowid

                # Создаем основного пользователя для партнера
                if partner_data.get('create_user', True):
                    username = self.generate_partner_username(partner_data['company_name'])
                    success, password = self.create_partner_user(partner_id, username)
                    if success:
                        partner_data['auto_username'] = username
                        partner_data['auto_password'] = password
                    else:
                        partner_data['auto_username'] = "Не создан"
                        partner_data['auto_password'] = password  # Сообщение об ошибке

                self.connection.commit()
                return True, partner_id
        except pymysql.Error as e:
            print(f"Ошибка добавления партнера: {e}")
            self.connection.rollback()
            return False, None

    def generate_partner_username(self, company_name):
        """Генерация имени пользователя на основе названия компании"""
        base_name = ''.join(c for c in company_name if c.isalnum()).lower()[:10]
        random_suffix = ''.join(random.choice(string.digits) for _ in range(4))
        return f"{base_name}_{random_suffix}"

    def update_partner(self, partner_id, partner_data):
        """Обновление данных партнера"""
        try:
            with self.connection.cursor() as cursor:
                query = """
                    UPDATE partners
                    SET company_name = %s, email = %s, contact_phone = %s, 
                        director_name = %s, inn = %s, partner_type_id = %s
                    WHERE partner_id = %s
                """
                values = (
                    partner_data['company_name'],
                    partner_data['email'],
                    partner_data['phone'],
                    partner_data['contact_person'],
                    partner_data.get('inn', ''),
                    partner_data['partner_type_id'],
                    partner_id
                )
                cursor.execute(query, values)
                self.connection.commit()
                return True
        except pymysql.Error as e:
            print(f"Ошибка обновления партнера: {e}")
            self.connection.rollback()
            return False

    def delete_partner(self, partner_id):
        """Удаление партнера из базы данных"""
        try:
            with self.connection.cursor() as cursor:
                # Сначала удаляем пользователя партнера
                cursor.execute("DELETE FROM users WHERE partner_id = %s", (partner_id,))
                # Затем удаляем партнера
                cursor.execute("DELETE FROM partners WHERE partner_id = %s", (partner_id,))
                self.connection.commit()
                return True
        except pymysql.Error as e:
            print(f"Ошибка удаления партнера: {e}")
            self.connection.rollback()
            return False

    def close_connection(self):
        """Закрытие подключения к базе данных"""
        if self.connection and self.connection.open:
            self.connection.close()
            print("Подключение к базе данных закрыто")


class PartnerUserDialog(QDialog):
    """Диалог для управления пользователем партнера"""

    def __init__(self, parent=None, partner_data=None, user_data=None):
        super().__init__(parent)
        self.partner_data = partner_data
        self.user_data = user_data
        self.is_edit = user_data is not None
        self.init_ui()

    def init_ui(self):
        title = "Редактирование пользователя" if self.is_edit else "Создание пользователя"
        self.setWindowTitle(f"{title} - {self.partner_data['company_name']}")
        self.setFixedSize(400, 250)

        layout = QVBoxLayout()

        # Форма
        form_layout = QFormLayout()

        self.username_edit = QLineEdit()
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.generate_password_cb = QCheckBox("Сгенерировать автоматически")

        if self.is_edit:
            self.username_edit.setText(self.user_data.get('username', ''))
            self.generate_password_cb.setChecked(False)
            self.password_edit.setPlaceholderText("Оставьте пустым, чтобы не менять пароль")
        else:
            self.generate_password_cb.setChecked(True)
            self.password_edit.setEnabled(False)

        self.generate_password_cb.stateChanged.connect(self.toggle_password_field)

        form_layout.addRow("Логин*:", self.username_edit)
        form_layout.addRow("Пароль:", self.password_edit)
        form_layout.addRow("", self.generate_password_cb)

        layout.addLayout(form_layout)

        # Кнопки
        button_layout = QHBoxLayout()
        self.save_btn = QPushButton("Сохранить")
        self.cancel_btn = QPushButton("Отмена")

        self.save_btn.clicked.connect(self.save_user)
        self.cancel_btn.clicked.connect(self.reject)

        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.cancel_btn)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def toggle_password_field(self):
        """Включение/выключение поля пароля"""
        self.password_edit.setEnabled(not self.generate_password_cb.isChecked())
        if self.generate_password_cb.isChecked():
            self.password_edit.clear()

    def save_user(self):
        """Сохранение пользователя"""
        username = self.username_edit.text().strip()

        if not username:
            QMessageBox.warning(self, "Ошибка", "Логин обязателен для заполнения!")
            return

        password = None
        if not self.generate_password_cb.isChecked() and self.password_edit.text():
            password = self.password_edit.text()

        self.result_data = {
            'username': username,
            'password': password
        }

        self.accept()


class PartnerUserManagementDialog(QDialog):
    """Диалог управления пользователем партнера (один пользователь на партнера)"""

    def __init__(self, parent=None, partner_data=None):
        super().__init__(parent)
        self.partner_data = partner_data
        self.user_data = None
        self.init_ui()
        self.load_user()

    def init_ui(self):
        self.setWindowTitle(f"Управление пользователем - {self.partner_data['company_name']}")
        self.setFixedSize(500, 300)

        layout = QVBoxLayout()

        # Информация о партнере
        info_group = QGroupBox("Информация о партнере")
        info_layout = QFormLayout()
        info_layout.addRow("Компания:", QLabel(self.partner_data['company_name']))
        info_layout.addRow("ИНН:", QLabel(self.partner_data.get('inn', '')))
        info_layout.addRow("Директор:", QLabel(self.partner_data.get('director_name', '')))
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        # Информация о пользователе
        self.user_group = QGroupBox("Пользователь")
        user_layout = QVBoxLayout()

        self.user_info_label = QLabel("Пользователь не создан")
        self.user_info_label.setStyleSheet("color: red; font-weight: bold;")

        user_buttons_layout = QHBoxLayout()
        self.create_user_btn = QPushButton("Создать пользователя")
        self.edit_user_btn = QPushButton("Редактировать")
        self.reset_password_btn = QPushButton("Сбросить пароль")
        self.delete_user_btn = QPushButton("Удалить пользователя")

        self.create_user_btn.clicked.connect(self.create_user)
        self.edit_user_btn.clicked.connect(self.edit_user)
        self.reset_password_btn.clicked.connect(self.reset_password)
        self.delete_user_btn.clicked.connect(self.delete_user)

        user_buttons_layout.addWidget(self.create_user_btn)
        user_buttons_layout.addWidget(self.edit_user_btn)
        user_buttons_layout.addWidget(self.reset_password_btn)
        user_buttons_layout.addWidget(self.delete_user_btn)

        user_layout.addWidget(self.user_info_label)
        user_layout.addLayout(user_buttons_layout)

        self.user_group.setLayout(user_layout)
        layout.addWidget(self.user_group)

        # Кнопка закрытия
        button_layout = QHBoxLayout()
        self.close_btn = QPushButton("Закрыть")
        self.close_btn.clicked.connect(self.accept)
        button_layout.addStretch()
        button_layout.addWidget(self.close_btn)

        layout.addLayout(button_layout)

        self.setLayout(layout)
        self.update_ui_state()

    def load_user(self):
        """Загрузка пользователя партнера"""
        self.user_data = self.parent().db.get_partner_user(self.partner_data['partner_id'])
        self.update_ui_state()

    def update_ui_state(self):
        """Обновление состояния UI в зависимости от наличия пользователя"""
        if self.user_data:
            self.user_info_label.setText(
                f"Логин: {self.user_data['username']}\n"
                f"Роль: {self.user_data.get('role_name', 'Partner_User')}"
            )
            self.user_info_label.setStyleSheet("color: green; font-weight: bold;")
            self.create_user_btn.setEnabled(False)
            self.edit_user_btn.setEnabled(True)
            self.reset_password_btn.setEnabled(True)
            self.delete_user_btn.setEnabled(True)
        else:
            self.user_info_label.setText("Пользователь не создан")
            self.user_info_label.setStyleSheet("color: red; font-weight: bold;")
            self.create_user_btn.setEnabled(True)
            self.edit_user_btn.setEnabled(False)
            self.reset_password_btn.setEnabled(False)
            self.delete_user_btn.setEnabled(False)

    def create_user(self):
        """Создание пользователя"""
        dialog = PartnerUserDialog(self, self.partner_data)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            user_data = dialog.result_data
            success, message = self.parent().db.create_partner_user(
                self.partner_data['partner_id'],
                user_data['username'],
                user_data.get('password')
            )
            if success:
                QMessageBox.information(self, "Успех", f"Пользователь создан. Пароль: {message}")
                self.load_user()
            else:
                QMessageBox.warning(self, "Ошибка", message)

    def edit_user(self):
        """Редактирование пользователя"""
        if not self.user_data:
            return

        dialog = PartnerUserDialog(self, self.partner_data, self.user_data)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            user_data = dialog.result_data
            success, message = self.parent().db.update_partner_user(
                self.user_data['user_id'], user_data
            )
            if success:
                QMessageBox.information(self, "Успех", message)
                self.load_user()
            else:
                QMessageBox.warning(self, "Ошибка", message)

    def reset_password(self):
        """Сброс пароля пользователя"""
        if not self.user_data:
            return

        reply = QMessageBox.question(
            self,
            "Подтверждение сброса",
            "Вы уверены, что хотите сбросить пароль пользователя?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            success, message = self.parent().db.reset_partner_user_password(self.user_data['user_id'])
            if success:
                QMessageBox.information(self, "Успех", f"Новый пароль: {message}")
            else:
                QMessageBox.warning(self, "Ошибка", message)

    def delete_user(self):
        """Удаление пользователя"""
        if not self.user_data:
            return

        reply = QMessageBox.question(
            self,
            "Подтверждение удаления",
            f"Вы уверены, что хотите удалить пользователя '{self.user_data['username']}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            if self.parent().db.delete_partner_user(self.user_data['user_id']):
                QMessageBox.information(self, "Успех", "Пользователь успешно удален")
                self.load_user()
            else:
                QMessageBox.critical(self, "Ошибка", "Не удалось удалить пользователя")


# Класс PartnerDialog остается без изменений
class PartnerDialog(QDialog):
    """Диалог для добавления/редактирования партнера"""

    def __init__(self, parent=None, partner_data=None):
        super().__init__(parent)
        self.partner_data = partner_data
        self.is_edit = partner_data is not None
        self.partner_types = []
        self.init_ui()
        self.load_partner_types()

    def init_ui(self):
        self.setWindowTitle("Редактирование партнера" if self.is_edit else "Добавление партнера")
        self.setFixedSize(450, 400)

        layout = QFormLayout()

        # Поля ввода
        self.name_edit = QLineEdit()
        self.email_edit = QLineEdit()
        self.phone_edit = QLineEdit()
        self.inn_edit = QLineEdit()
        self.contact_person_edit = QLineEdit()
        self.partner_type_combo = QComboBox()
        self.create_user_cb = QCheckBox("Создать пользователя по умолчанию")
        self.create_user_cb.setChecked(True)

        # Установка значений если редактируем
        if self.is_edit:
            self.name_edit.setText(self.partner_data.get('company_name', ''))
            self.email_edit.setText(self.partner_data.get('email', ''))
            self.phone_edit.setText(self.partner_data.get('contact_phone', ''))
            self.inn_edit.setText(self.partner_data.get('inn', ''))
            self.contact_person_edit.setText(self.partner_data.get('director_name', ''))
            self.create_user_cb.setVisible(False)

        # Добавление полей в форму
        layout.addRow("Название компании*:", self.name_edit)
        layout.addRow("Тип организации*:", self.partner_type_combo)
        layout.addRow("ИНН*:", self.inn_edit)
        layout.addRow("Директор*:", self.contact_person_edit)
        layout.addRow("Email:", self.email_edit)
        layout.addRow("Телефон:", self.phone_edit)
        if not self.is_edit:
            layout.addRow("", self.create_user_cb)

        # Кнопки
        button_layout = QHBoxLayout()
        self.save_btn = QPushButton("Сохранить")
        self.cancel_btn = QPushButton("Отмена")

        self.save_btn.clicked.connect(self.save_partner)
        self.cancel_btn.clicked.connect(self.reject)

        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.cancel_btn)

        layout.addRow(button_layout)

        self.setLayout(layout)

    def load_partner_types(self):
        """Загрузка типов организаций из базы данных"""
        try:
            self.partner_types = self.parent().db.get_partner_types()
            self.partner_type_combo.clear()

            for partner_type in self.partner_types:
                self.partner_type_combo.addItem(partner_type['type_name'], partner_type['type_id'])

            if self.is_edit and self.partner_data:
                current_type_id = self.partner_data.get('partner_type_id')
                if current_type_id:
                    index = self.partner_type_combo.findData(current_type_id)
                    if index >= 0:
                        self.partner_type_combo.setCurrentIndex(index)
            else:
                if self.partner_type_combo.count() > 0:
                    self.partner_type_combo.setCurrentIndex(0)

        except Exception as e:
            print(f"Ошибка загрузки типов партнеров: {e}")

    def save_partner(self):
        """Сохранение данных партнера"""
        name = self.name_edit.text().strip()
        inn = self.inn_edit.text().strip()
        contact_person = self.contact_person_edit.text().strip()
        partner_type_id = self.partner_type_combo.currentData()

        if not name:
            QMessageBox.warning(self, "Ошибка", "Название компании обязательно для заполнения!")
            return

        if not inn:
            QMessageBox.warning(self, "Ошибка", "ИНН обязателен для заполнения!")
            return

        if not contact_person:
            QMessageBox.warning(self, "Ошибка", "ФИО директора обязательно для заполнения!")
            return

        if not partner_type_id:
            QMessageBox.warning(self, "Ошибка", "Выберите тип организации!")
            return

        self.result_data = {
            'company_name': name,
            'email': self.email_edit.text().strip(),
            'phone': self.phone_edit.text().strip(),
            'inn': inn,
            'contact_person': contact_person,
            'partner_type_id': partner_type_id,
            'create_user': self.create_user_cb.isChecked() if not self.is_edit else False
        }

        self.accept()


class PartnerManager(QMainWindow):
    """Главное окно менеджера партнеров"""

    def __init__(self):
        super().__init__()
        self.current_user = {'user_id': 1, 'username': 'admin'}
        self.db = DatabaseManager()
        if not self.db.connection:
            QMessageBox.critical(self, "Ошибка", "Не удалось подключиться к базе данных!")
            sys.exit(1)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Менеджер партнеров - Master Floor")
        self.setGeometry(100, 100, 1200, 700)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()

        # Заголовок
        header_layout = QHBoxLayout()
        title_label = QLabel("Управление партнерами - Master Floor")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))

        user_buttons_layout = QHBoxLayout()
        self.manage_user_btn = QPushButton("Управление пользователем")
        self.logout_btn = QPushButton("Выйти")

        self.manage_user_btn.clicked.connect(self.manage_partner_user)
        self.logout_btn.clicked.connect(self.logout)

        user_buttons_layout.addWidget(self.manage_user_btn)
        user_buttons_layout.addWidget(self.logout_btn)

        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addLayout(user_buttons_layout)

        main_layout.addLayout(header_layout)

        # Панель кнопок
        button_layout = QHBoxLayout()

        self.add_btn = QPushButton("Добавить партнера")
        self.edit_btn = QPushButton("Редактировать")
        self.delete_btn = QPushButton("Удалить")
        self.refresh_btn = QPushButton("Обновить")

        self.add_btn.clicked.connect(self.add_partner)
        self.edit_btn.clicked.connect(self.edit_partner)
        self.delete_btn.clicked.connect(self.delete_partner)
        self.refresh_btn.clicked.connect(self.refresh_table)

        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.edit_btn)
        button_layout.addWidget(self.delete_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.refresh_btn)

        main_layout.addLayout(button_layout)

        # Разделитель
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        main_layout.addWidget(separator)

        # Таблица партнеров
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "ID", "Название компании", "Тип организации", "ИНН", "Директор", "Телефон", "Email", "Пользователь"
        ])

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)

        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        main_layout.addWidget(self.table)

        self.statusBar().showMessage("Готово к работе")

        central_widget.setLayout(main_layout)

        self.refresh_table()

    def manage_partner_user(self):
        """Управление пользователем выбранного партнера"""
        try:
            selected_row = self.table.currentRow()
            if selected_row == -1:
                QMessageBox.warning(self, "Ошибка", "Выберите партнера для управления пользователем!")
                return

            partner_id = int(self.table.item(selected_row, 0).text())
            partners = self.db.get_all_partners()
            partner_data = next((p for p in partners if p['partner_id'] == partner_id), None)

            if partner_data:
                dialog = PartnerUserManagementDialog(self, partner_data)
                dialog.exec()
        except Exception as e:
            print(f"Ошибка управления пользователем: {e}")
            QMessageBox.critical(self, "Ошибка", f"Ошибка при управлении пользователем: {str(e)}")

    def logout(self):
        """Выход из системы"""
        reply = QMessageBox.question(
            self,
            "Подтверждение выхода",
            "Вы уверены, что хотите выйти из системы?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.db.close_connection()
            self.close()

    def refresh_table(self):
        """Обновление таблицы из базы данных"""
        try:
            partners = self.db.get_all_partners()
            self.table.setRowCount(0)

            for partner in partners:
                row_position = self.table.rowCount()
                self.table.insertRow(row_position)

                self.table.setItem(row_position, 0, QTableWidgetItem(str(partner['partner_id'])))
                self.table.setItem(row_position, 1, QTableWidgetItem(partner['company_name']))
                self.table.setItem(row_position, 2, QTableWidgetItem(partner.get('partner_type_name', '')))
                self.table.setItem(row_position, 3, QTableWidgetItem(partner.get('inn', '')))
                self.table.setItem(row_position, 4, QTableWidgetItem(partner.get('director_name', '')))
                self.table.setItem(row_position, 5, QTableWidgetItem(partner.get('contact_phone', '')))
                self.table.setItem(row_position, 6, QTableWidgetItem(partner.get('email', '')))

                # Отображаем информацию о пользователе
                username = partner.get('username', '')
                user_count = partner.get('user_count', 0)
                if user_count > 0 and username:
                    user_text = username
                elif user_count > 0:
                    user_text = "Есть пользователь"
                else:
                    user_text = "Нет пользователя"

                self.table.setItem(row_position, 7, QTableWidgetItem(user_text))

            self.statusBar().showMessage(f"Загружено партнеров: {len(partners)}")
        except Exception as e:
            print(f"Ошибка обновления таблицы: {e}")
            QMessageBox.critical(self, "Ошибка", f"Ошибка при загрузке данных: {str(e)}")

    def add_partner(self):
        """Добавление нового партнера"""
        try:
            dialog = PartnerDialog(self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                new_partner = dialog.result_data

                success, partner_id = self.db.add_partner(new_partner)
                if success:
                    self.refresh_table()
                    message = f"Партнер '{new_partner['company_name']}' успешно добавлен"
                    if 'auto_username' in new_partner and 'auto_password' in new_partner:
                        if new_partner['auto_username'] != "Не создан":
                            message += f"\n\nАвтоматически создан пользователь:\nЛогин: {new_partner['auto_username']}\nПароль: {new_partner['auto_password']}"
                        else:
                            message += f"\n\nНе удалось создать пользователя: {new_partner['auto_password']}"
                    QMessageBox.information(self, "Успех", message)
                else:
                    QMessageBox.critical(self, "Ошибка", "Не удалось добавить партнера в базу данных")
        except Exception as e:
            print(f"Ошибка добавления партнера: {e}")
            QMessageBox.critical(self, "Ошибка", f"Ошибка при добавлении партнера: {str(e)}")

    def edit_partner(self):
        """Редактирование выбранного партнера"""
        try:
            selected_row = self.table.currentRow()
            if selected_row == -1:
                QMessageBox.warning(self, "Ошибка", "Выберите партнера для редактирования!")
                return

            partner_id = int(self.table.item(selected_row, 0).text())
            partner_name = self.table.item(selected_row, 1).text()

            partners = self.db.get_all_partners()
            partner_data = next((p for p in partners if p['partner_id'] == partner_id), None)

            if partner_data:
                dialog = PartnerDialog(self, partner_data)
                if dialog.exec() == QDialog.DialogCode.Accepted:
                    updated_data = dialog.result_data

                    if self.db.update_partner(partner_id, updated_data):
                        self.refresh_table()
                        QMessageBox.information(self, "Успех", "Данные партнера успешно обновлены")
                    else:
                        QMessageBox.critical(self, "Ошибка", "Не удалось обновить данные партнера")
        except Exception as e:
            print(f"Ошибка редактирования партнера: {e}")
            QMessageBox.critical(self, "Ошибка", f"Ошибка при редактировании партнера: {str(e)}")

    def delete_partner(self):
        """Удаление выбранного партнера"""
        try:
            selected_row = self.table.currentRow()
            if selected_row == -1:
                QMessageBox.warning(self, "Ошибка", "Выберите партнера для удаления!")
                return

            partner_id = int(self.table.item(selected_row, 0).text())
            partner_name = self.table.item(selected_row, 1).text()

            reply = QMessageBox.question(
                self,
                "Подтверждение удаления",
                f"Вы уверены, что хотите удалить партнера '{partner_name}'? (Пользователь также будет удален)",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                if self.db.delete_partner(partner_id):
                    self.refresh_table()
                    QMessageBox.information(self, "Успех", "Партнер и его пользователь успешно удалены")
                else:
                    QMessageBox.critical(self, "Ошибка", "Не удалось удалить партнера из базы данных")
        except Exception as e:
            print(f"Ошибка удаления партнера: {e}")
            QMessageBox.critical(self, "Ошибка", f"Ошибка при удалении партнера: {str(e)}")

    def closeEvent(self, event):
        """Обработчик закрытия приложения"""
        self.db.close_connection()
        event.accept()


def main():
    try:
        app = QApplication(sys.argv)
        app.setStyle('Fusion')

        window = PartnerManager()
        window.show()

        sys.exit(app.exec())
    except Exception as e:
        print(f"Критическая ошибка: {e}")
        QMessageBox.critical(None, "Ошибка", f"Критическая ошибка приложения: {str(e)}")


if __name__ == '__main__':
    main()
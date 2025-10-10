# windows/base_window.py

from PyQt6.QtWidgets import QMainWindow, QMessageBox


# from db.database_connector import get_db_connector # Если нужно проверять статус БД

class BaseWindow(QMainWindow):
    def __init__(self, user_role_id):
        super().__init__()

        # Сохраняем роль пользователя, чтобы использовать ее для управления доступом
        self.user_role = user_role_id

        self.setWindowTitle("ERP System Manager")
        self.apply_common_styles()  # Метод для применения QSS
        self.setup_status_bar()  # Инициализация строки статуса

        # Можно сразу проверить права
        # self.check_access_permissions()

    def apply_common_styles(self):
        """Здесь будет код для загрузки общего QSS файла."""
        # self.setStyleSheet(load_qss_file("styles/common.qss"))
        pass

    def show_error_message(self, title, message):
        """Метод, который могут вызвать все дочерние окна."""
        QMessageBox.critical(self, title, message)

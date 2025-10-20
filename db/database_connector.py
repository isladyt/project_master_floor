# db/database_connector.py

# ИСПОЛЬЗУЕМ PyMySQL ВМЕСТО mysql.connector ДЛЯ ОБХОДА СИСТЕМНОЙ ОШИБКИ 0xC0000005
import pymysql.cursors as mysql_connector_errors
import pymysql

from config import DB_CONFIG  # Используем настройки, которые мы прописали в config.py


# --- Класс для управления соединением ---
class DatabaseConnector:

    def __init__(self):
        """Инициализирует коннектор, но соединение пока не устанавливает."""
        self.connection = None
        self.cursor = None
        # PyMySQL по умолчанию возвращает строки как словари, если указать курсор-фабрику
        self.cursor_factory = pymysql.cursors.DictCursor

    def connect(self):
        """Устанавливает соединение с MySQL, используя DB_CONFIG."""
        try:
            # Пытаемся установить соединение
            self.connection = pymysql.connect(
                # PyMySQL требует, чтобы параметры передавались явно, а не через **kwargs
                host=DB_CONFIG["host"],
                user=DB_CONFIG["user"],
                password=DB_CONFIG["password"],
                database=DB_CONFIG["database"],
                cursorclass=self.cursor_factory # Используем DictCursor
            )
            self.cursor = self.connection.cursor()
            print("База данных: Соединение успешно установлено (через PyMySQL).")
            return True
        except mysql_connector_errors.Error as err:
            # PyMySQL использует свою иерархию ошибок, но мы можем поймать общий Error
            print(f"Ошибка при подключении к базе данных (PyMySQL): {err}")
            self.connection = None
            self.cursor = None
            return False

    def disconnect(self):
        """Закрывает соединение с БД."""
        if self.connection and self.connection.open:
            self.cursor.close()
            self.connection.close()
            print("База данных: Соединение закрыто.")

    def execute_query(self, query, params=None, fetch=False, commit=False):
        """
        Выполняет SQL-запрос.
        :param query: SQL-запрос (строка)
        :param params: Параметры для подстановки в запрос (кортеж или список)
        :param fetch: True, если нужно вернуть результат (SELECT)
        :param commit: True, если нужно сохранить изменения (INSERT, UPDATE, DELETE)
        """
        # PyMySQL использует 'open' вместо 'is_connected()'
        if not self.connection or not self.connection.open:
            print("Ошибка: Соединение с БД отсутствует или потеряно.")
            return None if fetch else False

        try:
            # PyMySQL использует '%s' как плейсхолдер
            self.cursor.execute(query.replace('%s', '%s'), params or ())

            if commit:
                self.connection.commit()
                return self.cursor.lastrowid if 'INSERT INTO' in query.upper() else True

            if fetch:
                return self.cursor.fetchall()

            return True

        except mysql_connector_errors.Error as err:
            # Откатываем изменения в случае ошибки
            if self.connection:
                self.connection.rollback()
            print(f"Ошибка выполнения запроса (PyMySQL): {err}")
            return None if fetch else False


# --- Функция-помощник для получения экземпляра ---
# Используется, чтобы не создавать новый объект при каждом обращении
connector = DatabaseConnector()


def get_db_connector():
    """Возвращает один и тот же экземпляр коннектора (синглтон)."""
    return connector

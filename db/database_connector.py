# db/database_connector.py

import mysql.connector
from config import DB_CONFIG  # Используем настройки, которые мы прописали в config.py


# --- Класс для управления соединением ---
class DatabaseConnector:

    def __init__(self):
        """Инициализирует коннектор, но соединение пока не устанавливает."""
        self.connection = None
        self.cursor = None

    def connect(self):
        """Устанавливает соединение с MySQL, используя DB_CONFIG."""
        try:
            # Пытаемся установить соединение
            self.connection = mysql.connector.connect(**DB_CONFIG)
            self.cursor = self.connection.cursor(
                dictionary=True)  # dictionary=True возвращает результат как список словарей
            print("База данных: Соединение успешно установлено.")
            return True
        except mysql.connector.Error as err:
            print(f"Ошибка при подключении к базе данных: {err}")
            self.connection = None
            self.cursor = None
            return False

    def disconnect(self):
        """Закрывает соединение с БД."""
        if self.connection and self.connection.is_connected():
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
        if not self.connection or not self.connection.is_connected():
            print("Ошибка: Соединение с БД отсутствует или потеряно.")
            return None if fetch else False

        try:
            self.cursor.execute(query, params or ())

            if commit:
                self.connection.commit()
                return self.cursor.lastrowid if 'INSERT INTO' in query.upper() else True  # Возвращаем ID для INSERT

            if fetch:
                return self.cursor.fetchall()

            return True  # Для успешных не-SELECT запросов без коммита

        except mysql.connector.Error as err:
            # Откатываем изменения в случае ошибки
            if self.connection:
                self.connection.rollback()
            print(f"Ошибка выполнения запроса: {err}")
            return None if fetch else False


# --- Функция-помощник для получения экземпляра ---
# Используется, чтобы не создавать новый объект при каждом обращении
connector = DatabaseConnector()


def get_db_connector():
    """Возвращает один и тот же экземпляр коннектора (синглтон)."""
    return connector

# ВАЖНО: Эту функцию будут вызывать твои models.py
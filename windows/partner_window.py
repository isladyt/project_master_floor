import sys
from PyQt6.QtWidgets import QMainWindow, QTableWidgetItem, QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

# Импорт функций для работы с БД
from db.models import get_all_products
from db import get_db_connector

# КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ ИМПОРТА UI
from ui_files.Ui_PartnerWindow import Ui_MainWindow as Ui_PartnerWindow


# КЛЮЧЕВОЕ ИСПРАВЛЕНИЕ: НАСЛЕДУЕМСЯ ТОЛЬКО ОТ QMainWindow
class PartnerWindow(QMainWindow):
    """
    Окно для Партнера, отображающее список доступных товаров.
    Просмотр без сортировки и поиска.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        # 1. ИСПОЛЬЗУЕМ КОМПОЗИЦИЮ: Создаем экземпляр UI-класса
        self.ui = Ui_PartnerWindow()
        self.ui.setupUi(self)

        # 2. Настройка таблицы
        self.setup_table_style()

        # 3. ИНИЦИАЛИЗАЦИЯ И ПРОВЕРКА СОЕДИНЕНИЯ С БД
        self.db_connector = get_db_connector()
        if not self.db_connector.connect():
            # Если соединение не удалось, показываем ошибку в таблице и выходим
            self.show_connection_error()
            return

        # 4. Загрузка данных (только если соединение установлено)
        try:
            self.load_products_data()
        except Exception as e:
            # Общий перехват для других потенциальных ошибок при работе с данными
            print(f"Критическая ошибка при загрузке данных: {e}")
            self.show_connection_error(f"Ошибка при загрузке данных: {e}")

    def show_connection_error(self, message="Ошибка подключения к базе данных. Проверьте настройки в config.py."):
        """Отображает сообщение об ошибке в таблице."""
        table_widget = self.ui.products_table
        table_widget.setRowCount(1)
        table_widget.setColumnCount(1)
        table_widget.setHorizontalHeaderLabels([""])
        empty_item = QTableWidgetItem(message)
        empty_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        table_widget.setItem(0, 0, empty_item)
        table_widget.horizontalHeader().setSectionResizeMode(0, table_widget.horizontalHeader().ResizeMode.Stretch)
        # Также можно закрыть приложение, если ошибка критическая, но лучше показать UI.

    def setup_table_style(self):
        """Базовая настройка внешнего вида QTableWidget."""
        # ДОСТУП К ТАБЛИЦЕ ЧЕРЕЗ self.ui.products_table
        table = self.ui.products_table

        # Запрет редактирования ячеек
        table.setEditTriggers(table.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(table.SelectionBehavior.SelectRows)
        table.setSelectionMode(table.SelectionMode.SingleSelection)

        # Стиль заголовка (можно настроить, используя CSS-подобный синтаксис)
        header = table.horizontalHeader()
        header.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        header.setStyleSheet("::section { background-color: #555555; color: white; padding: 5px; }")

    def load_products_data(self):
        """
        Загружает данные о товарах из базы данных и отображает их в QTableWidget.
        """
        # Получаем данные из models.py
        products = get_all_products()

        # ДОСТУП К ТАБЛИЦЕ ЧЕРЕЗ self.ui
        table_widget = self.ui.products_table

        # Очистка таблицы перед заполнением
        table_widget.setRowCount(0)

        if products:
            # 1. Заголовки столбцов (ДОЛЖНЫ СООТВЕТСТВОВАТЬ ПОРЯДКУ ПОЛЕЙ В SQL-ЗАПРОСЕ)
            headers = ["ID Товара", "Название", "Тип Продукции", "Мин. Цена (руб.)"]

            table_widget.setColumnCount(len(headers))
            table_widget.setHorizontalHeaderLabels(headers)
            table_widget.setRowCount(len(products))

            # 2. Заполнение таблицы
            for row_index, product in enumerate(products):
                # Порядок полей из словаря: id, name, product_type, price
                data_row = [
                    product.get('id'),
                    product.get('name'),
                    product.get('product_type'),
                    f"{product.get('price'):,.2f}"  # Форматируем цену для красоты
                ]

                for col_index, item_data in enumerate(data_row):
                    item = QTableWidgetItem(str(item_data))

                    # Выравнивание цены по правому краю
                    if col_index == 3:
                        item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

                    table_widget.setItem(row_index, col_index, item)

            # 3. Настройка внешнего вида таблицы
            table_widget.resizeColumnsToContents()
            table_widget.horizontalHeader().setStretchLastSection(True)

        else:
            # Если данных нет, но соединение прошло, показываем, что товаров нет
            table_widget.setRowCount(1)
            table_widget.setColumnCount(1)
            table_widget.setHorizontalHeaderLabels([""])
            empty_item = QTableWidgetItem("Нет доступных товаров.")
            empty_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            table_widget.setItem(0, 0, empty_item)

            # Растягивание колонки для центрирования сообщения
            table_widget.horizontalHeader().setSectionResizeMode(0, table_widget.horizontalHeader().ResizeMode.Stretch)



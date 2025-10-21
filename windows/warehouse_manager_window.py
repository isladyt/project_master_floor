import sys
from PyQt6.QtWidgets import (QMainWindow, QTableWidgetItem, QApplication,
                             QMessageBox, QDialog, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QComboBox, QPushButton, QDialogButtonBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QDoubleValidator

# Импорт функций для работы с БД
from db.models import get_all_products, update_product
from db import get_db_connector

# Импорт UI
from ui_files.Ui_WarehouseWindow  import Ui_MainWindow as Ui_PartnerWindow


class EditProductDialog(QDialog):
    """Диалог для редактирования товара"""

    def __init__(self, product_data, parent=None):
        super().__init__(parent)
        self.product_data = product_data
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Редактирование товара")
        self.setModal(True)
        self.resize(400, 300)

        layout = QVBoxLayout()

        # Поля для редактирования
        self.id_label = QLabel(f"ID товара: {self.product_data['id']}")
        layout.addWidget(self.id_label)

        layout.addWidget(QLabel("Название:"))
        self.name_edit = QLineEdit(self.product_data['name'])
        layout.addWidget(self.name_edit)

        layout.addWidget(QLabel("Тип продукции:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Электроника", "Одежда", "Книги", "Продукты", "Другое"])
        current_type = self.product_data['product_type']
        index = self.type_combo.findText(current_type)
        if index >= 0:
            self.type_combo.setCurrentIndex(index)
        layout.addWidget(self.type_combo)

        layout.addWidget(QLabel("Цена:"))
        self.price_edit = QLineEdit(str(self.product_data['price']))
        price_validator = QDoubleValidator(0.0, 999999.99, 2)
        self.price_edit.setValidator(price_validator)
        layout.addWidget(self.price_edit)

        # Кнопки
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok |
                                      QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)

    def get_updated_data(self):
        """Возвращает обновленные данные товара"""
        return {
            'id': self.product_data['id'],
            'name': self.name_edit.text().strip(),
            'product_type': self.type_combo.currentText(),
            'price': float(self.price_edit.text())
        }


class WarehouseManagerWindow(QMainWindow):
    """
    Окно для Менеджера склада с функциями:
    - Просмотр товаров
    - Сортировка по колонкам
    - Редактирование товаров
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        # Создаем экземпляр UI-класса
        self.ui = Ui_PartnerWindow()
        self.ui.setupUi(self)

        # Переименовываем элементы для ясности
        self.products_table = self.ui.tableWidget
        self.edit_button = self.ui.pushButton
        self.sort_combo = self.ui.comboBox

        # Настройка интерфейса
        self.setup_ui()

        # Инициализация и проверка соединения с БД
        self.db_connector = get_db_connector()
        if not self.db_connector.connect():
            self.show_connection_error()
            return

        # Загрузка данных
        try:
            self.load_products_data()
        except Exception as e:
            print(f"Критическая ошибка при загрузке данных: {e}")
            self.show_connection_error(f"Ошибка при загрузке данных: {e}")

    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        self.setWindowTitle("Управление складом - Менеджер")

        # Настройка таблицы
        self.setup_table_style()

        # Настройка комбобокса сортировки
        self.setup_sort_combo()

        # Подключение сигналов
        self.edit_button.clicked.connect(self.edit_selected_product)
        self.products_table.itemDoubleClicked.connect(self.edit_selected_product)

        # Включаем сортировку в таблице
        self.products_table.setSortingEnabled(True)

    def setup_table_style(self):
        """Настройка внешнего вида таблицы"""
        # Разрешаем редактирование (будет управляться через диалог)
        self.products_table.setEditTriggers(self.products_table.EditTrigger.NoEditTriggers)
        self.products_table.setSelectionBehavior(self.products_table.SelectionBehavior.SelectRows)
        self.products_table.setSelectionMode(self.products_table.SelectionMode.SingleSelection)

        # Стиль заголовка
        header = self.products_table.horizontalHeader()
        header.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        header.setStyleSheet("::section { background-color: #555555; color: white; padding: 5px; }")

        # Подключаем двойной клик по заголовку для сортировки
        header.sectionDoubleClicked.connect(self.on_header_double_clicked)

    def setup_sort_combo(self):
        """Настройка комбобокса для сортировки"""
        sort_options = [
            "Без сортировки",
            "По названию (А-Я)",
            "По названию (Я-А)",
            "По типу (А-Я)",
            "По типу (Я-А)",
            "По цене (возрастание)",
            "По цене (убывание)"
        ]

        self.sort_combo.clear()
        self.sort_combo.addItems(sort_options)
        self.sort_combo.currentIndexChanged.connect(self.apply_sorting)

    def on_header_double_clicked(self, logical_index):
        """Обработка двойного клика по заголовку для сортировки"""
        if logical_index in [1, 2, 3]:  # Колонки: Название, Тип, Цена
            current_order = self.products_table.horizontalHeader().sortIndicatorOrder()
            if current_order == Qt.SortOrder.AscendingOrder:
                self.products_table.sortByColumn(logical_index, Qt.SortOrder.DescendingOrder)
            else:
                self.products_table.sortByColumn(logical_index, Qt.SortOrder.AscendingOrder)

    def apply_sorting(self):
        """Применение выбранной сортировки"""
        sort_index = self.sort_combo.currentIndex()

        if sort_index == 0:  # Без сортировки
            self.products_table.sortByColumn(-1, Qt.SortOrder.AscendingOrder)
        elif sort_index == 1:  # По названию (А-Я)
            self.products_table.sortByColumn(1, Qt.SortOrder.AscendingOrder)
        elif sort_index == 2:  # По названию (Я-А)
            self.products_table.sortByColumn(1, Qt.SortOrder.DescendingOrder)
        elif sort_index == 3:  # По типу (А-Я)
            self.products_table.sortByColumn(2, Qt.SortOrder.AscendingOrder)
        elif sort_index == 4:  # По типу (Я-А)
            self.products_table.sortByColumn(2, Qt.SortOrder.DescendingOrder)
        elif sort_index == 5:  # По цене (возрастание)
            self.products_table.sortByColumn(3, Qt.SortOrder.AscendingOrder)
        elif sort_index == 6:  # По цене (убывание)
            self.products_table.sortByColumn(3, Qt.SortOrder.DescendingOrder)

    def show_connection_error(self, message="Ошибка подключения к базе данных."):
        """Отображает сообщение об ошибке в таблице"""
        self.products_table.setRowCount(1)
        self.products_table.setColumnCount(1)
        self.products_table.setHorizontalHeaderLabels([""])
        empty_item = QTableWidgetItem(message)
        empty_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.products_table.setItem(0, 0, empty_item)
        self.products_table.horizontalHeader().setSectionResizeMode(0,
                                                                    self.products_table.horizontalHeader().ResizeMode.Stretch)

    def load_products_data(self):
        """Загружает данные о товарах из базы данных"""
        products = get_all_products()
        self.original_products = products  # Сохраняем оригинальные данные

        # Очистка таблицы перед заполнением
        self.products_table.setRowCount(0)

        if products:
            # Заголовки столбцов
            headers = ["ID Товара", "Название", "Тип Продукции", "Цена (руб.)"]
            self.products_table.setColumnCount(len(headers))
            self.products_table.setHorizontalHeaderLabels(headers)
            self.products_table.setRowCount(len(products))

            # Заполнение таблицы
            for row_index, product in enumerate(products):
                data_row = [
                    product.get('id'),
                    product.get('name'),
                    product.get('product_type'),
                    product.get('price')  # Храним как число для корректной сортировки
                ]

                for col_index, item_data in enumerate(data_row):
                    if col_index == 3:  # Колонка цены
                        item = QTableWidgetItem(f"{item_data:,.2f}")
                        item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                        # Сохраняем оригинальное значение для сортировки
                        item.setData(Qt.ItemDataRole.UserRole, item_data)
                    else:
                        item = QTableWidgetItem(str(item_data))

                    self.products_table.setItem(row_index, col_index, item)

            # Настройка внешнего вида таблицы
            self.products_table.resizeColumnsToContents()
            self.products_table.horizontalHeader().setStretchLastSection(True)

            # Устанавливаем начальную сортировку по ID
            self.products_table.sortByColumn(0, Qt.SortOrder.AscendingOrder)

        else:
            # Если данных нет
            self.products_table.setRowCount(1)
            self.products_table.setColumnCount(1)
            self.products_table.setHorizontalHeaderLabels([""])
            empty_item = QTableWidgetItem("Нет доступных товаров.")
            empty_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.products_table.setItem(0, 0, empty_item)
            self.products_table.horizontalHeader().setSectionResizeMode(0,
                                                                        self.products_table.horizontalHeader().ResizeMode.Stretch)

    def edit_selected_product(self):
        """Редактирование выбранного товара"""
        selected_row = self.products_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Внимание", "Пожалуйста, выберите товар для редактирования.")
            return

        # Получаем ID товара из выбранной строки
        product_id_item = self.products_table.item(selected_row, 0)
        if not product_id_item:
            return

        product_id = int(product_id_item.text())

        # Находим полные данные товара
        product_data = None
        for product in self.original_products:
            if product['id'] == product_id:
                product_data = product
                break

        if not product_data:
            QMessageBox.warning(self, "Ошибка", "Не удалось найти данные товара.")
            return

        # Открываем диалог редактирования
        dialog = EditProductDialog(product_data, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            updated_data = dialog.get_updated_data()

            # Проверяем валидность данных
            if not updated_data['name']:
                QMessageBox.warning(self, "Ошибка", "Название товара не может быть пустым.")
                return

            try:
                price = float(updated_data['price'])
                if price < 0:
                    QMessageBox.warning(self, "Ошибка", "Цена не может быть отрицательной.")
                    return
            except ValueError:
                QMessageBox.warning(self, "Ошибка", "Некорректное значение цены.")
                return

            # Обновляем данные в БД
            try:
                success = update_product(
                    updated_data['id'],
                    updated_data['name'],
                    updated_data['product_type'],
                    updated_data['price']
                )

                if success:
                    QMessageBox.information(self, "Успех", "Товар успешно обновлен.")
                    # Перезагружаем данные
                    self.load_products_data()
                else:
                    QMessageBox.warning(self, "Ошибка", "Не удалось обновить товар в базе данных.")

            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Произошла ошибка при обновлении: {str(e)}")

    def refresh_data(self):
        """Обновление данных в таблице"""
        try:
            self.load_products_data()
            QMessageBox.information(self, "Успех", "Данные обновлены.")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось обновить данные: {str(e)}")

def main():
    app = QApplication(sys.argv)
    window = WarehouseManagerWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
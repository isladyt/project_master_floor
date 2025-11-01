# windows/supplier_manager_window.py

import sys
import os
from PyQt6.QtWidgets import (QMainWindow, QMessageBox, QTableWidgetItem, QHeaderView)
from PyQt6.uic import loadUi
from PyQt6.QtCore import Qt

# Добавляем путь для импорта
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from db import get_all_suppliers, add_new_supplier, edit_supplier_info, delete_supplier, get_supplier_by_id


class SupplierManagerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Загружаем интерфейс
        ui_path = os.path.join(os.path.dirname(__file__), '..', 'ui', 'supplier_manager.ui')
        loadUi(ui_path, self)

        self.current_supplier_id = None
        self.setup_ui()
        self.load_suppliers()
        self.connect_signals()

    def setup_ui(self):
        """Настройка интерфейса"""
        # Настраиваем таблицу
        self.suppliers_table.setColumnCount(4)
        self.suppliers_table.setHorizontalHeaderLabels([
            "ID", "Название компании", "ИНН", "Контактный телефон"
        ])

        # Настраиваем растяжение колонок
        header = self.suppliers_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)

        # Таблица только для чтения
        self.suppliers_table.setEditTriggers(self.suppliers_table.EditTrigger.NoEditTriggers)

    def connect_signals(self):
        """Подключаем сигналы"""
        self.add_button.clicked.connect(self.add_supplier)
        self.edit_button.clicked.connect(self.edit_supplier)
        self.delete_button.clicked.connect(self.delete_supplier)
        self.clear_button.clicked.connect(self.clear_form)
        self.suppliers_table.itemSelectionChanged.connect(self.on_supplier_selected)

    def load_suppliers(self):
        """Загружаем список поставщиков"""
        suppliers = get_all_suppliers()
        self.suppliers_table.setRowCount(len(suppliers))

        for row, supplier in enumerate(suppliers):
            self.suppliers_table.setItem(row, 0, QTableWidgetItem(str(supplier['supplier_id'])))
            self.suppliers_table.setItem(row, 1, QTableWidgetItem(supplier['company_name']))
            self.suppliers_table.setItem(row, 2, QTableWidgetItem(supplier['inn']))
            phone = supplier.get('contact_phone', '')
            self.suppliers_table.setItem(row, 3, QTableWidgetItem(phone))

    def on_supplier_selected(self):
        """Обработчик выбора поставщика"""
        selected_items = self.suppliers_table.selectedItems()
        if not selected_items:
            return

        row = selected_items[0].row()
        self.current_supplier_id = int(self.suppliers_table.item(row, 0).text())

        # Заполняем форму данными
        supplier = get_supplier_by_id(self.current_supplier_id)
        if supplier:
            self.company_name_edit.setText(supplier['company_name'])
            self.inn_edit.setText(supplier['inn'])
            self.phone_edit.setText(supplier.get('contact_phone', ''))

    def validate_form(self):
        """Проверяем форму"""
        company_name = self.company_name_edit.text().strip()
        inn = self.inn_edit.text().strip()

        if not company_name:
            QMessageBox.warning(self, "Ошибка", "Введите название компании")
            return False

        if not inn:
            QMessageBox.warning(self, "Ошибка", "Введите ИНН")
            return False

        if not inn.isdigit():
            QMessageBox.warning(self, "Ошибка", "ИНН должен содержать только цифры")
            return False

        return True

    def get_form_data(self):
        """Получаем данные из формы"""
        return {
            'company_name': self.company_name_edit.text().strip(),
            'inn': self.inn_edit.text().strip(),
            'contact_phone': self.phone_edit.text().strip()
        }

    def add_supplier(self):
        """Добавляем поставщика"""
        if not self.validate_form():
            return

        supplier_data = self.get_form_data()

        try:
            result = add_new_supplier(supplier_data)
            if result:
                QMessageBox.information(self, "Успех", "Поставщик успешно добавлен")
                self.clear_form()
                self.load_suppliers()
            else:
                QMessageBox.critical(self, "Ошибка", "Не удалось добавить поставщика")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при добавлении: {str(e)}")

    def edit_supplier(self):
        """Редактируем поставщика"""
        if not self.current_supplier_id:
            QMessageBox.warning(self, "Ошибка", "Выберите поставщика для редактирования")
            return

        if not self.validate_form():
            return

        supplier_data = self.get_form_data()

        try:
            result = edit_supplier_info(self.current_supplier_id, supplier_data)
            if result:
                QMessageBox.information(self, "Успех", "Данные поставщика обновлены")
                self.clear_form()
                self.load_suppliers()
            else:
                QMessageBox.critical(self, "Ошибка", "Не удалось обновить данные")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при обновлении: {str(e)}")

    def delete_supplier(self):
        """Удаляем поставщика"""
        if not self.current_supplier_id:
            QMessageBox.warning(self, "Ошибка", "Выберите поставщика для удаления")
            return

        reply = QMessageBox.question(
            self,
            "Подтверждение удаления",
            "Вы уверены, что хотите удалить этого поставщика?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                result = delete_supplier(self.current_supplier_id)
                if result:
                    QMessageBox.information(self, "Успех", "Поставщик удален")
                    self.clear_form()
                    self.load_suppliers()
                else:
                    QMessageBox.critical(self, "Ошибка", "Не удалось удалить поставщика")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка при удалении: {str(e)}")

    def clear_form(self):
        """Очищаем форму"""
        self.current_supplier_id = None
        self.company_name_edit.clear()
        self.inn_edit.clear()
        self.phone_edit.clear()
        self.suppliers_table.clearSelection()
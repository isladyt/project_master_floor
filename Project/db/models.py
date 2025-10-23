# db/models.py

from .database_connector import get_db_connector


def get_all_suppliers():
    """Возвращает список всех поставщиков товара."""
    db = get_db_connector()

    query = "SELECT * FROM suppliers ORDER BY company_name"
    result = db.execute_query(query, fetch=True)
    return result or []


def add_new_supplier(supplier_data):
    """Добавляет нового поставщика."""
    db = get_db_connector()

    query = "INSERT INTO suppliers (company_name, inn, contact_phone) VALUES (%s, %s, %s)"
    params = (
        supplier_data['company_name'],
        supplier_data['inn'],
        supplier_data.get('contact_phone', '')
    )
    result = db.execute_query(query, params, commit=True)
    return result is not False


def edit_supplier_info(supplier_id, new_data):
    """Редактирует данные существующего поставщика."""
    db = get_db_connector()

    query = "UPDATE suppliers SET company_name = %s, inn = %s, contact_phone = %s WHERE supplier_id = %s"
    params = (
        new_data['company_name'],
        new_data['inn'],
        new_data.get('contact_phone', ''),
        supplier_id
    )
    result = db.execute_query(query, params, commit=True)
    return result is not False


def delete_supplier(supplier_id):
    """Удаляет поставщика."""
    db = get_db_connector()

    query = "DELETE FROM suppliers WHERE supplier_id = %s"
    result = db.execute_query(query, (supplier_id,), commit=True)
    return result is not False


def get_supplier_by_id(supplier_id):
    """Возвращает данные поставщика по ID."""
    db = get_db_connector()

    query = "SELECT * FROM suppliers WHERE supplier_id = %s"
    result = db.execute_query(query, (supplier_id,), fetch=True)
    return result[0] if result else None
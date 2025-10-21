# db/models.py
from .database_connector import get_db_connector
def get_user_by_login(login, password):
    """Проверяет учетные данные и возвращает данные пользователя (ID, роль) или None."""
    pass

def register_new_user(user_data):
    """Добавляет нового пользователя в БД."""
    pass

def update_product(product_id, name, product_type, price):
    """
    Обновляет данные товара в базе данных
    """
    pass


def get_all_products(sort_by=None, filter_by=None):
    """
    Возвращает список товаров, с опциональной сортировкой и фильтрацией.
    Для Окна Партнера вызывается без параметров.
    """
    db_connector = get_db_connector()

    # 1. SQL-запрос для получения товаров
    # Запрос должен соответствовать заголовкам столбцов в UI: ID, Название, Тип, Цена
    query = """
    SELECT 
        p.product_id AS id, 
        p.product_name AS name, 
        pt.type_name AS product_type, 
        p.min_partner_price AS price
    FROM 
        products p
    JOIN 
        product_types pt ON p.product_type_id = pt.type_id
    """

    # 2. Выполнение запроса
    # Мы полагаемся на db_connector.execute_query, который уже содержит
    # логику проверки соединения (connection.open для PyMySQL) и обработки ошибок.
    products = db_connector.execute_query(query, fetch=True)

    if products is None or products is False:
        # Если была ошибка выполнения или соединение было потеряно
        print("Ошибка при получении данных о товарах или нет соединения с БД.")
        return []

    return products

def get_product_by_id(product_id):
    """Возвращает данные одного товара по его ID."""
    pass

def update_product_data(product_id, new_data):
    """Редактирует информацию о товаре."""
    pass

def get_all_partners():
    """Возвращает список всех партнеров."""
    pass

def add_new_partner(partner_data):
    """Добавляет нового партнера в систему."""
    pass

def edit_partner_info(partner_id, new_data):
    """Редактирует данные существующего партнера."""
    pass

def add_production_order(order_data):
    """Создает новый заказ на изготовление."""
    pass

def get_production_report(date_start, date_end):
    """Генерирует отчетность по производству за период (оплата, закупки)."""
    pass

def record_customer_payment(order_id, amount):
    """Отмечает оплату от заказчика по конкретному заказу."""
    pass

def get_all_suppliers():
    """Возвращает список всех поставщиков товара."""
    pass

def add_new_supplier(supplier_data):
    """Добавляет нового поставщика."""
    pass

def edit_supplier_info(supplier_id, new_data):
    """Редактирует данные существующего поставщика."""
    pass

def get_all_employees():
    """Возвращает список всех работников."""
    pass

def add_new_employee(employee_data):
    """Добавляет нового работника."""
    pass

def edit_employee_info(employee_id, new_data):
    """Редактирует данные существующего работника."""
    pass

def log_turnstile_event(employee_id, event_type):
    """Записывает событие прохода через турникет (приход/уход)."""
    pass

def get_employee_movement_report(employee_id=None, date_range=None):
    """Ведет учет передвижения: возвращает отчет о приходах/уходах."""
    pass
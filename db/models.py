# db/models.py
from .database_connector import get_db_connector

# ОТЛАДОЧНАЯ ФУНКЦИЯ
def debug_check_users():
    """Отладочная функция для проверки пользователей в БД"""
    db = get_db_connector()
    if not db.connect():
        print("ОШИБКА: Не удалось подключиться к БД")
        return
    
    query = "SELECT user_id, username, password_hash, role_id FROM users"
    result = db.execute_query(query, fetch=True)
    print("=== ВСЕ ПОЛЬЗОВАТЕЛИ В БД ===")
    if result:
        for user in result:
            print(f"ID: {user['user_id']}, Логин: '{user['username']}', Пароль: '{user['password_hash']}', Роль: {user['role_id']}")
    else:
        print("В БД нет пользователей")
    print("==============================")
    return result

# ФУНКЦИИ АВТОРИЗАЦИИ
def get_user_by_login(username, password):
    """Проверяет учетные данные и возвращает данные пользователя (ID, роль) или None."""
    db = get_db_connector()
    print(f"Попытка подключения к БД для пользователя: '{username}'")  # ОТЛАДКА
    
    if not db.connect():
        print("ОШИБКА: Не удалось подключиться к БД")  # ОТЛАДКА
        return None
        
    # В реальном приложении здесь должно быть хеширование пароля
    # Но для теста работаем с открытым паролем
    query = "SELECT user_id, username, role_id FROM users WHERE username=%s AND password_hash=%s"
    print(f"Выполняем запрос: {query} с параметрами: '{username}', '{password}'")  # ОТЛАДКА
    
    result = db.execute_query(query, (username, password), fetch=True)
    print(f"Результат запроса: {result}")  # ОТЛАДКА
    
    if result:
        print(f"Найден пользователь: {result[0]}")  # ОТЛАДКА
    else:
        print("Пользователь не найден или неверный пароль")  # ОТЛАДКА
    
    return result[0] if result else None

def check_username_exists(username):
    """Проверить существование пользователя с таким логином"""
    db = get_db_connector()
    query = "SELECT user_id FROM users WHERE username = %s"
    result = db.execute_query(query, (username,), fetch=True)
    return bool(result)

def check_inn_exists(inn):
    """Проверить существование партнера с таким ИНН"""
    db = get_db_connector()
    query = "SELECT partner_id FROM partners WHERE inn = %s"
    result = db.execute_query(query, (inn,), fetch=True)
    return bool(result)

def register_new_user(user_data):
    """Добавляет нового пользователя в БД."""
    db = get_db_connector()
    print(f"Регистрация нового пользователя: {user_data}")  # ОТЛАДКА
    
    if not db.connect():
        print("ОШИБКА: Не удалось подключиться к БД при регистрации")  # ОТЛАДКА
        return False, "Ошибка подключения к базе данных"
    
    # Проверяем, существует ли пользователь с таким логином
    if check_username_exists(user_data['username']):
        print(f"Логин '{user_data['username']}' уже существует")  # ОТЛАДКА
        return False, "Пользователь с таким логином уже существует"
    
    # Проверяем, существует ли партнер с таким ИНН
    if check_inn_exists(user_data['inn']):
        print(f"ИНН '{user_data['inn']}' уже существует")  # ОТЛАДКА
        return False, "Партнер с таким ИНН уже зарегистрирован"

    try:
        # Создаем партнера
        query_partner = """
            INSERT INTO partners (company_name, inn, director_name, email, partner_type_id)
            VALUES (%s, %s, %s, %s, %s)
        """
        partner_values = (
            user_data['company_name'],
            user_data['inn'],
            user_data['director_name'],
            user_data['email'],
            1  # тип партнера по умолчанию
        )
        print(f"Создаем партнера: {query_partner} с значениями: {partner_values}")  # ОТЛАДКА
        
        partner_result = db.execute_query(query_partner, partner_values, commit=True)
        if partner_result is False:
            print("ОШИБКА: Не удалось создать партнера")  # ОТЛАДКА
            return False, "Ошибка при создании партнера"

        # Получаем ID созданного партнера через SELECT LAST_INSERT_ID()
        partner_id_result = db.execute_query("SELECT LAST_INSERT_ID() AS partner_id", fetch=True)
        if not partner_id_result:
            print("ОШИБКА: Не удалось получить ID созданного партнера")  # ОТЛАДКА
            return False, "Ошибка при получении ID партнера"
            
        partner_id = partner_id_result[0]['partner_id']
        print(f"Создан партнер с ID: {partner_id}")  # ОТЛАДКА

        # Создаем пользователя
        query_user = """
            INSERT INTO users (partner_id, username, password_hash, role_id)
            VALUES (%s, %s, %s, %s)
        """
        user_values = (
            partner_id,
            user_data['username'],
            user_data['password_hash'],  # Сохраняем пароль как есть (без хеширования)
            user_data['role_id']  # всегда Partner
        )
        print(f"Создаем пользователя: {query_user} с значениями: {user_values}")  # ОТЛАДКА
        
        user_result = db.execute_query(query_user, user_values, commit=True)
        
        if user_result is False:
            print("ОШИБКА: Не удалось создать пользователя")  # ОТЛАДКА
            return False, "Ошибка при создании пользователя"
        
        print("Регистрация прошла успешно!")  # ОТЛАДКА
        return True, "Регистрация прошла успешно"
        
    except Exception as e:
        print(f"Ошибка при регистрации: {e}")  # ОТЛАДКА
        return False, f"Ошибка при регистрации: {str(e)}"

# СУЩЕСТВУЮЩИЕ ФУНКЦИИ (НЕ МЕНЯЕМ)
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

# config.py

# --- Настройки Базы Данных (MySQL) ---
DB_CONFIG = {
    "host": "localhost",
    "user": "pycharm_user",             # Твой пользователь MySQL
    "password": "strong_secret_password", # Твой пароль
    "database": "erp_project_db",       # Имя твоей базы данных
    "port": 3306                        # Порт (обычно 3306)
}

# --- Общие Константы Приложения ---
APP_NAME = "ERP System Manager"

# Роли пользователей для управления доступом
USER_ROLES = {
    1: "Partner",
    2: "WarehouseManager",
    3: "PartnerManager",
    4: "ProductionManager",
    5: "ProcurementManager",
    6: "HRManager"
}
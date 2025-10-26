# windows/__init__.py

# Импортируем все основные классы окон, как только ты их создашь
from .registration_window import RegistrationWindow
from .partner_window import PartnerWindow # Раскомментируешь потом
# from .warehouse_manager_window import WarehouseManagerWindow # Раскомментируешь потом
# ... и так далее для всех окон

# windows/__init__.py
from .base_window import BaseWindow
from .registration_window import RegistrationWindow

__all__ = ['BaseWindow', 'RegistrationWindow']

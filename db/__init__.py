# db/__init__.py

# Эти импорты позволяют тебе писать, например:
# from db import connect_to_db вместо from db.database_connector import connect_to_db

from .database_connector import get_db_connector
from .models import get_user_by_login, get_all_products
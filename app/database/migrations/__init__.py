"""Миграции базы данных."""

# Порядок применения миграций
MIGRATION_ORDER = [
    "001_initial",
    "002_add_feedback", 
    "003_add_indexing"
]

def get_migration_order():
    """Возвращает порядок применения миграций."""
    return MIGRATION_ORDER

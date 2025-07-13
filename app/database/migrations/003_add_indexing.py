"""Добавление индексов для оптимизации производительности."""
from alembic import op
import sqlalchemy as sa

revision = "003_add_indexing"
down_revision = "002_add_feedback"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Добавление индексов."""
    
    # Индексы для таблицы users
    op.create_index("ix_users_is_member", "users", ["is_member"])
    op.create_index("ix_users_org_member", "users", ["organization_name", "is_member"])
    op.create_index("ix_users_registration_date", "users", ["registration_date"])
    
    # Индексы для таблицы messages
    op.create_index("ix_messages_session_timestamp", "messages", ["session_id", "timestamp"])
    op.create_index("ix_messages_processing_time", "messages", ["processing_time"])
    op.create_index("ix_messages_user_message_fts", "messages", ["user_message"], postgresql_using="gin", postgresql_ops={"user_message": "gin_trgm_ops"})
    
    # Индексы для таблицы documents
    op.create_index("ix_documents_type_active", "documents", ["document_type", "is_active"])
    op.create_index("ix_documents_category_active", "documents", ["category", "is_active"])
    op.create_index("ix_documents_public_active", "documents", ["is_public", "is_active"])
    op.create_index("ix_documents_title_fts", "documents", ["title"], postgresql_using="gin", postgresql_ops={"title": "gin_trgm_ops"})
    op.create_index("ix_documents_upload_updated", "documents", ["upload_date", "last_updated"])
    op.create_index("ix_documents_download_count", "documents", ["download_count"])
    
    # Индексы для таблицы sessions
    op.create_index("ix_sessions_user_active", "sessions", ["user_id", "is_active"])
    op.create_index("ix_sessions_created_active", "sessions", ["created_at", "is_active"])
    op.create_index("ix_sessions_last_activity", "sessions", ["last_activity"])
    op.create_index("ix_sessions_duration", "sessions", ["created_at", "session_end"])
    
    # Составные индексы для сложных запросов
    op.create_index("ix_messages_session_user_timestamp", "messages", ["session_id", "timestamp"])
    op.create_index("ix_documents_type_category_active", "documents", ["document_type", "category", "is_active"])
    op.create_index("ix_feedback_user_type_created", "feedback", ["user_id", "feedback_type", "created_at"])
    
    # Частичные индексы для активных записей
    op.create_index("ix_sessions_active_only", "sessions", ["user_id", "last_activity"], postgresql_where="is_active = true")
    op.create_index("ix_documents_active_only", "documents", ["title", "upload_date"], postgresql_where="is_active = true")
    
    # Индексы для полнотекстового поиска (PostgreSQL)
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")
    op.execute("CREATE EXTENSION IF NOT EXISTS btree_gin;")


def downgrade() -> None:
    """Удаление индексов."""
    
    # Удаляем индексы для таблицы users
    op.drop_index("ix_users_is_member")
    op.drop_index("ix_users_org_member")
    op.drop_index("ix_users_registration_date")
    
    # Удаляем индексы для таблицы messages
    op.drop_index("ix_messages_session_timestamp")
    op.drop_index("ix_messages_processing_time")
    op.drop_index("ix_messages_user_message_fts")
    
    # Удаляем индексы для таблицы documents
    op.drop_index("ix_documents_type_active")
    op.drop_index("ix_documents_category_active")
    op.drop_index("ix_documents_public_active")
    op.drop_index("ix_documents_title_fts")
    op.drop_index("ix_documents_upload_updated")
    op.drop_index("ix_documents_download_count")
    
    # Удаляем индексы для таблицы sessions
    op.drop_index("ix_sessions_user_active")
    op.drop_index("ix_sessions_created_active")
    op.drop_index("ix_sessions_last_activity")
    op.drop_index("ix_sessions_duration")
    
    # Удаляем составные индексы
    op.drop_index("ix_messages_session_user_timestamp")
    op.drop_index("ix_documents_type_category_active")
    op.drop_index("ix_feedback_user_type_created")
    
    # Удаляем частичные индексы
    op.drop_index("ix_sessions_active_only")
    op.drop_index("ix_documents_active_only")

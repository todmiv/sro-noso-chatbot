"""Добавление таблицы отзывов."""
from alembic import op
import sqlalchemy as sa

revision = "002_add_feedback"
down_revision = "001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Создание таблицы feedback."""
    op.create_table(
        "feedback",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False, index=True),
        sa.Column("message_id", sa.Integer, sa.ForeignKey("messages.id"), nullable=True, index=True),
        sa.Column("rating", sa.Integer, nullable=False, index=True),
        sa.Column("comment", sa.Text, nullable=True),
        sa.Column("feedback_type", sa.String(50), nullable=False, index=True),
        sa.Column("category", sa.String(100), nullable=True, index=True),
        sa.Column("created_at", sa.DateTime, default=sa.func.now(), index=True),
        sa.Column("is_processed", sa.Boolean, default=False, index=True),
        sa.Column("admin_response", sa.Text, nullable=True),
        sa.Column("processed_at", sa.DateTime, nullable=True),
        sa.Column("processed_by", sa.Integer, nullable=True),
    )
    
    # Добавляем индексы
    op.create_index("ix_feedback_rating_type", "feedback", ["rating", "feedback_type"])
    op.create_index("ix_feedback_created_processed", "feedback", ["created_at", "is_processed"])
    
    # Добавляем проверочные ограничения
    op.create_check_constraint(
        "check_feedback_rating",
        "feedback",
        "rating >= 1 AND rating <= 5"
    )
    
    op.create_check_constraint(
        "check_feedback_type",
        "feedback", 
        "feedback_type IN ('response', 'general', 'bug', 'feature')"
    )


def downgrade() -> None:
    """Удаление таблицы feedback."""
    op.drop_table("feedback")

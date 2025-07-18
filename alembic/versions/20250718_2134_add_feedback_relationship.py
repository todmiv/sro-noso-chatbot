"""Add feedback relationship to User model

Revision ID: 8a7b3c5d2e1f4a9b0c6d7e8f9a0b1c2d
Revises: e5daa2c7261d
Create Date: 2025-07-18 21:34:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8a7b3c5d2e1f4a9b0c6d7e8f9a0b1c2d'
down_revision = 'e5daa2c7261d'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # No schema changes needed - relationship is defined in models only
    pass


def downgrade() -> None:
    # No schema changes needed
    pass

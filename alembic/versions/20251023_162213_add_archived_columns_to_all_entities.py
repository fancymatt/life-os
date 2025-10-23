"""Add archived columns to all entities

Revision ID: 20251023_162213
Revises: a1b2c3d4e5f6
Create Date: 2025-10-23 16:22:13.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20251023_162213'
down_revision: Union[str, Sequence[str], None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - add archived and archived_at columns to all entity tables."""

    # List of tables that should support archiving
    tables = [
        'characters',
        'clothing_items',
        'board_games',
        'outfits',
        'stories',
        'story_scenes',
        'images',
        'visualization_configs',
        'compositions'
    ]

    for table in tables:
        # Add archived column (defaults to False for existing rows)
        op.add_column(table, sa.Column('archived', sa.Boolean(), nullable=False, server_default='false'))

        # Add archived_at column (nullable, only set when archived=true)
        op.add_column(table, sa.Column('archived_at', sa.DateTime(), nullable=True))

        # Add index for filtering archived entities
        op.create_index(
            f'ix_{table}_archived',
            table,
            ['archived'],
            unique=False
        )


def downgrade() -> None:
    """Downgrade schema - remove archived columns from all entity tables."""

    tables = [
        'characters',
        'clothing_items',
        'board_games',
        'outfits',
        'stories',
        'story_scenes',
        'images',
        'visualization_configs',
        'compositions'
    ]

    for table in tables:
        # Drop index
        op.drop_index(f'ix_{table}_archived', table_name=table)

        # Drop columns
        op.drop_column(table, 'archived_at')
        op.drop_column(table, 'archived')

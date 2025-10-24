"""add_modification_tracking_to_clothing_items

Revision ID: 13fba8c69581
Revises: b7920182b2a9
Create Date: 2025-10-24 04:14:50.823463

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '13fba8c69581'
down_revision: Union[str, Sequence[str], None] = 'b7920182b2a9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - Add modification tracking fields to clothing_items table."""
    # Add manually_modified column (default False)
    op.add_column('clothing_items', sa.Column('manually_modified', sa.Boolean(), nullable=False, server_default='false'))

    # Add source_entity_id column for variant tracking
    op.add_column('clothing_items', sa.Column('source_entity_id', sa.String(length=50), nullable=True))

    # Add index on source_entity_id for finding all variants of an entity
    op.create_index('ix_clothing_source_entity', 'clothing_items', ['source_entity_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema - Remove modification tracking fields."""
    # Drop index
    op.drop_index('ix_clothing_source_entity', table_name='clothing_items')

    # Drop columns
    op.drop_column('clothing_items', 'source_entity_id')
    op.drop_column('clothing_items', 'manually_modified')

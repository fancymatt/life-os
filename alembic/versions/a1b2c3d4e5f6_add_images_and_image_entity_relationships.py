"""Add images and image_entity_relationships tables

Revision ID: a1b2c3d4e5f6
Revises: f85c460c4214
Create Date: 2025-10-22 19:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = 'f85c460c4214'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - add images and image_entity_relationships tables."""
    # Create images table
    op.create_table('images',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('image_id', sa.String(length=100), nullable=False),
        sa.Column('file_path', sa.String(length=500), nullable=False),
        sa.Column('filename', sa.String(length=255), nullable=False),
        sa.Column('width', sa.Integer(), nullable=True),
        sa.Column('height', sa.Integer(), nullable=True),
        sa.Column('generation_metadata', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_images_user_id_users')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_images'))
    )
    op.create_index(op.f('ix_images_image_id'), 'images', ['image_id'], unique=True)
    op.create_index('ix_image_user_created', 'images', ['user_id', 'created_at'], unique=False)

    # Create image_entity_relationships table
    op.create_table('image_entity_relationships',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('image_id', sa.String(length=100), nullable=False),
        sa.Column('entity_type', sa.String(length=100), nullable=False),
        sa.Column('entity_id', sa.String(length=100), nullable=False),
        sa.Column('role', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['image_id'], ['images.image_id'], name=op.f('fk_image_entity_relationships_image_id_images')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_image_entity_relationships'))
    )
    op.create_index(op.f('ix_image_entity_relationships_entity_id'), 'image_entity_relationships', ['entity_id'], unique=False)
    op.create_index(op.f('ix_image_entity_relationships_entity_type'), 'image_entity_relationships', ['entity_type'], unique=False)
    op.create_index(op.f('ix_image_entity_relationships_image_id'), 'image_entity_relationships', ['image_id'], unique=False)
    op.create_index(op.f('ix_image_entity_relationships_role'), 'image_entity_relationships', ['role'], unique=False)
    op.create_index('ix_relationship_entity', 'image_entity_relationships', ['entity_type', 'entity_id'], unique=False)
    op.create_index('ix_relationship_image', 'image_entity_relationships', ['image_id'], unique=False)
    op.create_index('ix_relationship_unique', 'image_entity_relationships', ['image_id', 'entity_type', 'entity_id', 'role'], unique=True)


def downgrade() -> None:
    """Downgrade schema - remove images and image_entity_relationships tables."""
    # Drop image_entity_relationships table
    op.drop_index('ix_relationship_unique', table_name='image_entity_relationships')
    op.drop_index('ix_relationship_image', table_name='image_entity_relationships')
    op.drop_index('ix_relationship_entity', table_name='image_entity_relationships')
    op.drop_index(op.f('ix_image_entity_relationships_role'), table_name='image_entity_relationships')
    op.drop_index(op.f('ix_image_entity_relationships_image_id'), table_name='image_entity_relationships')
    op.drop_index(op.f('ix_image_entity_relationships_entity_type'), table_name='image_entity_relationships')
    op.drop_index(op.f('ix_image_entity_relationships_entity_id'), table_name='image_entity_relationships')
    op.drop_table('image_entity_relationships')

    # Drop images table
    op.drop_index('ix_image_user_created', table_name='images')
    op.drop_index(op.f('ix_images_image_id'), table_name='images')
    op.drop_table('images')

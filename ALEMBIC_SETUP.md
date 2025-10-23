# Alembic Database Migration Setup

## What is Alembic?

Alembic is a database migration tool for SQLAlchemy that provides version control for your database schema. It allows you to:

- Track all database schema changes over time
- Apply changes incrementally (upgrade)
- Roll back changes if needed (downgrade)
- Auto-generate migrations from model changes
- Keep all environments in sync (dev, staging, production)

## Installation

Alembic is already in requirements.txt, so it's available in the Docker container.

## Initial Setup

### 1. Initialize Alembic

```bash
# Run inside the API container
docker exec -it ai-studio-api bash
cd /app
alembic init alembic
```

This creates:
```
alembic/
├── env.py              # Alembic environment configuration
├── script.py.mako      # Template for new migrations
└── versions/           # Migration files go here
alembic.ini             # Alembic configuration file
```

### 2. Configure alembic.ini

Edit `alembic.ini`:

```ini
# Line 63: Update database URL (or use environment variable)
sqlalchemy.url = postgresql+asyncpg://%(DB_USER)s:%(DB_PASSWORD)s@%(DB_HOST)s:%(DB_PORT)s/%(DB_NAME)s

# Or comment it out and set in env.py instead:
# sqlalchemy.url =
```

### 3. Configure env.py for Async Support

Edit `alembic/env.py`:

```python
import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# Import your models and Base
from api.models.db import Base
from api.database import get_database_url

# this is the Alembic Config object
config = context.config

# Set database URL from environment
config.set_main_option('sqlalchemy.url', get_database_url())

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Add your model's MetaData object here for 'autogenerate' support
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations in 'online' mode (async)."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

## Creating Migrations

### Auto-Generate from Models (Recommended)

When you change your models, Alembic can detect the changes:

```bash
# Generate migration from model changes
docker exec -w /app ai-studio-api alembic revision --autogenerate -m "Add favorites table"
```

This creates a file like: `alembic/versions/001_add_favorites_table.py`

### Manual Migration (for complex changes)

```bash
docker exec -w /app ai-studio-api alembic revision -m "Custom migration"
```

## Example Migration Files

### Migration 1: Initial Schema

`alembic/versions/001_initial_schema.py`:

```python
"""Initial schema with all tables

Revision ID: 001_abcd1234
Revises:
Create Date: 2025-10-22 17:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '001_abcd1234'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create all initial tables"""

    # Users table
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=True),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('disabled', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('last_login', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    # Characters table
    op.create_table('characters',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('character_id', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('visual_description', sa.Text(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_characters_character_id'), 'characters', ['character_id'], unique=True)

    # ... more tables ...


def downgrade() -> None:
    """Drop all tables (reverse of upgrade)"""
    op.drop_table('characters')
    op.drop_table('users')
    # ... drop other tables in reverse order ...
```

### Migration 2: Add Column

`alembic/versions/002_add_character_tags.py`:

```python
"""Add tags column to characters

Revision ID: 002_efgh5678
Revises: 001_abcd1234
Create Date: 2025-10-23 10:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '002_efgh5678'
down_revision = '001_abcd1234'  # Points to previous migration
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add tags column"""
    op.add_column('characters',
        sa.Column('tags', postgresql.JSON(), nullable=False, server_default='[]')
    )


def downgrade() -> None:
    """Remove tags column"""
    op.drop_column('characters', 'tags')
```

### Migration 3: Add Table

`alembic/versions/003_add_favorites_table.py`:

```python
"""Add favorites table

Revision ID: 003_ijkl9012
Revises: 002_efgh5678
Create Date: 2025-10-23 15:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = '003_ijkl9012'
down_revision = '002_efgh5678'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create favorites table"""
    op.create_table('favorites',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=False),
        sa.Column('preset_id', sa.String(length=100), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_favorite_user_category', 'favorites', ['user_id', 'category'])
    op.create_index('ix_favorite_unique', 'favorites', ['user_id', 'category', 'preset_id'], unique=True)


def downgrade() -> None:
    """Drop favorites table"""
    op.drop_index('ix_favorite_unique', table_name='favorites')
    op.drop_index('ix_favorite_user_category', table_name='favorites')
    op.drop_table('favorites')
```

### Migration 4: Data Migration

`alembic/versions/004_migrate_json_to_db.py`:

```python
"""Migrate data from JSON files to database

Revision ID: 004_mnop3456
Revises: 003_ijkl9012
Create Date: 2025-10-23 16:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
import json
from pathlib import Path

revision = '004_mnop3456'
down_revision = '003_ijkl9012'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Migrate favorites from JSON to database"""

    # Get connection
    connection = op.get_bind()

    # Read JSON file
    favorites_file = Path("/app/data/favorites.json")
    if favorites_file.exists():
        favorites_data = json.loads(favorites_file.read_text())

        # Insert into database
        for username, favorite_list in favorites_data.items():
            # Get user_id
            result = connection.execute(
                sa.text("SELECT id FROM users WHERE username = :username"),
                {"username": username}
            )
            user = result.fetchone()
            if not user:
                continue

            user_id = user[0]

            # Insert favorites
            for favorite in favorite_list:
                category, preset_id = favorite.split(':', 1)
                connection.execute(
                    sa.text("""
                        INSERT INTO favorites (user_id, category, preset_id, created_at)
                        VALUES (:user_id, :category, :preset_id, NOW())
                        ON CONFLICT DO NOTHING
                    """),
                    {"user_id": user_id, "category": category, "preset_id": preset_id}
                )


def downgrade() -> None:
    """Cannot reverse data migration"""
    pass  # Or export data back to JSON
```

## Running Migrations

### Check Current Status

```bash
# Show current database version
docker exec -w /app ai-studio-api alembic current

# Show migration history
docker exec -w /app ai-studio-api alembic history

# Show pending migrations
docker exec -w /app ai-studio-api alembic heads
```

### Apply Migrations

```bash
# Upgrade to latest version
docker exec -w /app ai-studio-api alembic upgrade head

# Upgrade one version at a time
docker exec -w /app ai-studio-api alembic upgrade +1

# Upgrade to specific version
docker exec -w /app ai-studio-api alembic upgrade 002_efgh5678
```

### Rollback Migrations

```bash
# Downgrade one version
docker exec -w /app ai-studio-api alembic downgrade -1

# Downgrade to specific version
docker exec -w /app ai-studio-api alembic downgrade 001_abcd1234

# Downgrade all the way
docker exec -w /app ai-studio-api alembic downgrade base
```

## Integration with Docker

Add to `docker-entrypoint.sh`:

```bash
#!/bin/bash
set -e

echo "🚀 Starting AI-Studio API..."

# Run database migrations
echo "📊 Running database migrations..."
alembic upgrade head

# Check if migration succeeded
if [ $? -eq 0 ]; then
    echo "✅ Database migrations completed"
else
    echo "❌ Database migrations failed"
    exit 1
fi

# Start the application
echo "✅ Starting FastAPI server..."
exec uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

This way, migrations run automatically on container startup!

## Workflow Example

### Scenario: Adding a new "Stories" feature

1. **Update your model**:
```python
# api/models/db.py
class Story(Base):
    __tablename__ = "stories"
    id: Mapped[int] = mapped_column(primary_key=True)
    story_id: Mapped[str] = mapped_column(String(50), unique=True)
    title: Mapped[str] = mapped_column(String(500))
    content: Mapped[str] = mapped_column(Text)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
```

2. **Generate migration**:
```bash
docker exec -w /app ai-studio-api alembic revision --autogenerate -m "Add stories table"
```

3. **Review the generated migration**:
```bash
cat alembic/versions/005_add_stories_table.py
```

4. **Apply migration**:
```bash
docker exec -w /app ai-studio-api alembic upgrade head
```

5. **Commit to Git**:
```bash
git add alembic/versions/005_add_stories_table.py
git commit -m "feat: Add stories table migration"
git push
```

6. **Deploy to production**:
```bash
# On production server
docker-compose pull
docker-compose up -d
# Migrations run automatically via entrypoint.sh
```

## Benefits for Your Project

1. **Version Control**: Every schema change is tracked in Git
2. **Team Collaboration**: Other developers can apply your migrations
3. **Production Safety**: Can test migrations on staging before production
4. **Rollback**: If something breaks, easily revert
5. **Documentation**: Migration files document schema evolution
6. **Automated**: Runs on container startup

## Current State

Right now, your database has all tables created, but Alembic doesn't know about them. To start using Alembic:

**Option 1: Start Fresh (Recommended for new projects)**
- Export current data
- Drop all tables
- Initialize Alembic
- Create initial migration
- Re-import data

**Option 2: Bootstrap from Current State**
- Initialize Alembic
- Mark current schema as baseline
- Future changes use migrations

I can help you set up either option!

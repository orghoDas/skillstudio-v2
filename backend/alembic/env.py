from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context
import asyncio

# ============================================
# Import Config and Models
# ============================================
from app.core.config import settings
from app.core.database import Base

# Import ALL models here so Alembic can detect them
from app.models.user import User
from app.models.learner_profile import LearnerProfile

# this is the Alembic Config object
config = context.config

# Override sqlalchemy.url with our settings from .env
config.set_main_option('sqlalchemy.url', settings.DATABASE_URL_SYNC)

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set target metadata to our Base (all our models)
target_metadata = Base.metadata


# ============================================
# Offline Migrations
# ============================================
def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.
    
    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well. By skipping the Engine creation
    we don't even need a DBAPI to be available.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


# ============================================
# Online Migrations (Async)
# ============================================
def do_run_migrations(connection: Connection) -> None:
    """Run migrations with a connection"""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,  # Detect column type changes
        compare_server_default=True,  # Detect default value changes
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """
    Run migrations in async mode using asyncpg
    """
    from sqlalchemy.ext.asyncio import create_async_engine
    
    # Create async engine for migrations
    connectable = create_async_engine(
        settings.DATABASE_URL,
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode.
    """
    asyncio.run(run_async_migrations())


# ============================================
# Main Entry Point
# ============================================
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
# alembic/env.py
import os
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine, pool

# --- Path & dotenv ------------------------------------------------------------
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(BASE_DIR)

from dotenv import load_dotenv
load_dotenv(os.path.join(BASE_DIR, ".env"))

# --- Import Base & models (agar terdaftar ke Base.metadata) -------------------
from src.database import Base
from src.auth import models as auth_models  # noqa: F401
from src.users import models as user_models  # noqa: F401   <-- add this line
# Jika ada model lain, import juga (biarkan tak terpakai; penting untuk discovery):
# from src.users import models as users_models  # noqa: F401
# from src.files import models as files_models  # noqa: F401

# --- Alembic config ------------------------------------------------------------
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

# --- Only use DATABASE_URL (tanpa fallback) -----------------------------------
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL is not set. Define it in .env (e.g. "
        "'postgresql+psycopg2://postgres:root@db:5432/tutuplapak_db')."
    )
# print(f"DEBUG Alembic DATABASE_URL: {DATABASE_URL}")  # optional

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = create_engine(
        DATABASE_URL,
        poolclass=pool.NullPool,
        pool_pre_ping=True,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

from __future__ import annotations
import os
import sys
from logging.config import fileConfig
from pathlib import Path

from sqlalchemy import engine_from_config, pool
from sqlalchemy.engine import Connection
from alembic import context

# optional: load .env so DATABASE_URL can come from there
try:
    from dotenv import load_dotenv
except Exception:
    load_dotenv = None

# Alembic Config object, provides access to .ini
config = context.config

# set up logging from config file if present
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ---------------------------
# Ensure project root is on sys.path so we can import models
# ---------------------------
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

# Load .env from project root if present (helps local dev)
env_path = project_root / ".env"
if load_dotenv is not None and env_path.exists():
    # load environment variables (DATABASE_URL etc.)
    load_dotenv(dotenv_path=str(env_path), override=False)

# --------------------------------------------------------------------------
# Import SQLAlchemy Base metadata (attempt common locations)
# --------------------------------------------------------------------------
target_metadata = None
_import_errors = []
for candidate in ("src.files.models", "src.models", "models", "app.models"):
    try:
        module = __import__(candidate, fromlist=["Base"])
        Base = getattr(module, "Base", None)
        if Base is not None:
            # Alembic will use this metadata for autogenerate
            target_metadata = Base.metadata
            break
    except Exception as e:
        _import_errors.append((candidate, repr(e)))
        continue

if target_metadata is None:
    # helpful warning — autogenerate will not work until metadata is found
    sys.stderr.write(
        "WARNING: Alembic could not import target metadata (Base) from candidates.\n"
        "Tried: {}\n".format(", ".join([c for c, _ in _import_errors]))
        + "If your models are located elsewhere, edit migrations/env.py to point to them.\n"
    )

# --------------------------------------------------------------------------
# Prefer DATABASE_URL from environment (.env). This overrides alembic.ini.
# --------------------------------------------------------------------------
db_url = os.environ.get("DATABASE_URL")
if db_url:
    config.set_main_option("sqlalchemy.url", db_url)

# ensure we have a URL to work with
url = config.get_main_option("sqlalchemy.url")
if not url:
    raise RuntimeError("sqlalchemy.url is not set in alembic.ini or DATABASE_URL")


# --------------------------------------------------------------------------
# Offline migrations (emit SQL without DB connection)
# --------------------------------------------------------------------------
def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.
    Generates SQL script without connecting to the database.
    """
    url = config.get_main_option("sqlalchemy.url")
    if not url:
        raise RuntimeError("DATABASE_URL not set for offline migrations")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


# --------------------------------------------------------------------------
# Online migrations (connect to the DB synchronously)
# --------------------------------------------------------------------------
def _run_migrations(connection: Connection) -> None:
    """
    Configure the migration context using a live Connection and run migrations.
    """
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode using a synchronous Engine created
    by engine_from_config(). This is the classic Alembic synchronous path.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    # connectable is a synchronous Engine; use normal connection context
    with connectable.connect() as connection:
        _run_migrations(connection)


# Entrypoint: choose offline or online mode
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

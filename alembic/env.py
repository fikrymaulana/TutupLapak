from __future__ import annotations
import os
import sys
from logging.config import fileConfig
from pathlib import Path
from typing import Sequence

from sqlalchemy import create_engine, pool
from sqlalchemy.engine import Connection
from alembic import context

try:
    from dotenv import load_dotenv  # type: ignore
except Exception:
    load_dotenv = None  # type: ignore

# Alembic Config object, provides access to .ini
config = context.config

# set up logging from config file if present
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# --------------------------------------------------------------------------
# Ensure project root & src on sys.path so we can import models
# --------------------------------------------------------------------------
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

env_path = project_root / ".env"
if load_dotenv is not None and env_path.exists():
    load_dotenv(dotenv_path=str(env_path), override=False)

# --------------------------------------------------------------------------
# Import SQLAlchemy Base metadata (try common locations)
# --------------------------------------------------------------------------
target_metadata = None
_import_errors: list[tuple[str, str]] = []
candidates: Sequence[str] = (
    "src.files.models",
    "src.models",
    "models",
    "app.models",
    "src.database",
)

for candidate in candidates:
    try:
        module = __import__(candidate, fromlist=["Base"])
        Base = getattr(module, "Base", None)
        if Base is not None:
            target_metadata = Base.metadata
            break
    except Exception as e:
        _import_errors.append((candidate, repr(e)))
        continue

if target_metadata is None:
    sys.stderr.write(
        "WARNING: Alembic could not import target metadata (Base) from candidates.\n"
        "Tried: {}\n".format(", ".join([c for c, _ in _import_errors]))
        + "If your models live in a different module, update migrations/env.py.\n"
    )

# --------------------------------------------------------------------------
# Prefer DATABASE_URL from environment (.env). This overrides alembic.ini.
# --------------------------------------------------------------------------
DATABASE_URL = os.environ.get("DATABASE_URL")
if DATABASE_URL:
    config.set_main_option("sqlalchemy.url", DATABASE_URL)

# final check for a URL
url = config.get_main_option("sqlalchemy.url")
if not url:
    raise RuntimeError("sqlalchemy.url is not set in alembic.ini or DATABASE_URL")


# --------------------------------------------------------------------------
# Offline migrations
# --------------------------------------------------------------------------
def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode (emit SQL scripts).
    """
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


# --------------------------------------------------------------------------
# Online migrations (synchronous)
# --------------------------------------------------------------------------
def _run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode using a synchronous Engine.
    """
    connectable = create_engine(
        url,  # type: ignore
        poolclass=pool.NullPool,
        pool_pre_ping=True,
    )

    with connectable.connect() as connection:
        _run_migrations(connection)


# Entrypoint: choose offline or online mode
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

# alembic/env.py
import os, sys
from logging.config import fileConfig
from alembic import context
from sqlalchemy import create_engine, pool

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(BASE_DIR)

from dotenv import load_dotenv
load_dotenv(os.path.join(BASE_DIR, ".env"))

# 1) Import Base lebih dulu
from src.database import Base

# 2) Import SEMUA modul yang mendefinisikan model (agar kelas2 model terdaftar ke Base.metadata)
from src.auth import models as auth_models  # noqa: F401
# kalau ada model lain:
# from src.users import models as users_models  # noqa: F401
# from src.files import models as files_models  # noqa: F401

# 3) Baru set metadata untuk Alembic
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

# 4) Ambil DATABASE_URL
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    host = os.getenv("POSTGRES_HOST", "db")
    user = os.getenv("POSTGRES_USER", "postgres")
    pwd = os.getenv("POSTGRES_PASSWORD", "root")
    dbname = os.getenv("POSTGRES_DB", "tutuplapak_db")
    DATABASE_URL = f"postgresql+psycopg2://{user}:{pwd}@{host}:5432/{dbname}"

print(f"DEBUG Alembic DATABASE_URL: {DATABASE_URL}")

def run_migrations_offline() -> None:
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    connectable = create_engine(DATABASE_URL, poolclass=pool.NullPool, pool_pre_ping=True)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

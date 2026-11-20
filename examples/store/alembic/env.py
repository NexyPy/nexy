"""Alembic env.py template - wires up target_metadata per ORM."""

import importlib
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import engine_from_config, pool

# Autogenerate compares the database with the models, so every `*_model.py` of `src/` is imported:
# a table whose module is not imported would be taken for one to drop.
PROJECT = Path(__file__).resolve().parent.parent
for model in sorted((PROJECT / "src").glob("**/*_model.py")):
    importlib.import_module(".".join(model.relative_to(PROJECT).with_suffix("").parts))

from src.configs.db import engine  # noqa: E402
from src.models.todo_model import Base  # noqa: E402

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    context.configure(
        url=engine.url,
        target_metadata=target_metadata,
        literal_binds=True,
        render_as_batch=engine.url.get_backend_name() == "sqlite",
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            # SQLite cannot ALTER a constraint: batch mode copies the table instead.
            render_as_batch=connection.dialect.name == "sqlite",
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

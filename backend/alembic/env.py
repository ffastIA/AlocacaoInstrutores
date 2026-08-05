"""Ambiente de migração do Alembic.

A URL do banco vem da configuração da aplicação, não do `alembic.ini`, para que
migração e runtime usem sempre o mesmo banco.
"""

from logging.config import fileConfig

from sqlalchemy import pool

from alembic import context
from app.core.config import settings
from app.db.base import Base
from app.db.session import criar_engine

# Importar os modelos registra todas as tabelas nos metadados da Base.
import app.models  # noqa: F401  isort:skip

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Gera o SQL das migrações sem conectar ao banco."""
    context.configure(
        url=settings.database_url_resolvida,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        # O SQLite não suporta ALTER de coluna; o modo batch recria a tabela.
        render_as_batch=True,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Aplica as migrações conectando ao banco."""
    settings.garantir_diretorios()
    connectable = criar_engine(poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=True,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()

    connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

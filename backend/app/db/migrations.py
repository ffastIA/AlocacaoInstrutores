"""Aplicação programática das migrações do Alembic.

Rodar as migrações na inicialização faz a aplicação subir com o banco pronto,
sem exigir um comando manual antes do primeiro uso.
"""

import logging
from pathlib import Path

from alembic.config import Config

from alembic import command
from app.core.config import settings

logger = logging.getLogger(__name__)

# Raiz do backend, dois níveis acima de app/db/.
RAIZ_BACKEND = Path(__file__).resolve().parents[2]


def aplicar_migracoes() -> None:
    """Aplica as migrações pendentes, criando o banco se ainda não existir."""
    settings.garantir_diretorios()

    config = Config(str(RAIZ_BACKEND / "alembic.ini"))
    config.set_main_option("script_location", str(RAIZ_BACKEND / "alembic"))

    logger.info("Aplicando migrações pendentes")
    command.upgrade(config, "head")
    logger.info("Banco atualizado")

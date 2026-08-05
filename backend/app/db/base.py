"""Base declarativa do SQLAlchemy.

Importar `Base` daqui e nunca do módulo de sessão: o Alembic precisa acessar os
metadados sem instanciar o engine.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass

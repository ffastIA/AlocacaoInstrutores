"""Engine, fábrica de sessões e dependência de injeção do FastAPI."""

from collections.abc import Generator

from sqlalchemy import Engine, create_engine, event
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings


def criar_engine(url: str | None = None, **kwargs: object) -> Engine:
    """Cria um engine SQLAlchemy com os ajustes necessários para SQLite.

    `kwargs` é repassado ao `create_engine` — o Alembic usa isso para pedir
    `poolclass=NullPool`.
    """
    url = url or settings.database_url_resolvida
    e_sqlite = url.startswith("sqlite")

    engine = create_engine(
        url,
        # O SQLite do Python bloqueia o uso da conexão fora da thread que a
        # criou. O FastAPI atende requisições em threads distintas, então a
        # checagem precisa ser desligada.
        connect_args={"check_same_thread": False} if e_sqlite else {},
        pool_pre_ping=True,
        **kwargs,
    )

    if e_sqlite:

        @event.listens_for(engine, "connect")
        def _configurar_sqlite(dbapi_connection, connection_record) -> None:  # noqa: ANN001
            cursor = dbapi_connection.cursor()
            # O SQLite ignora chaves estrangeiras a menos que sejam habilitadas
            # por conexão — sem isso a integridade referencial do esquema não
            # seria aplicada.
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    return engine


engine = criar_engine()

SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_db() -> Generator[Session, None, None]:
    """Fornece uma sessão por requisição, sempre encerrada ao final."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

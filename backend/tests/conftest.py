"""Fixtures dos testes.

Cada teste usa um banco SQLite isolado em arquivo temporário — o banco de
desenvolvimento nunca é tocado.
"""

from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

import app.models  # noqa: F401  registra as tabelas nos metadados
from app.core.config import settings
from app.db.base import Base
from app.db.session import criar_engine, get_db
from app.main import app


@pytest.fixture(autouse=True)
def _diretorio_cenarios_isolado(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Isola os JSONs de parâmetros de cenário num diretório temporário.

    Sem isso, qualquer teste que crie um cenário escreveria arquivos de
    verdade em `data/cenarios/`, poluindo o diretório de desenvolvimento.
    """
    monkeypatch.setattr(settings, "cenarios_dir", tmp_path / "cenarios")


@pytest.fixture
def engine(tmp_path: Path):
    """Engine sobre banco temporário, com o esquema já criado.

    Usa arquivo em vez de `:memory:` porque cada conexão a um banco em memória
    enxergaria um banco diferente.
    """
    url = f"sqlite:///{(tmp_path / 'teste.db').as_posix()}"
    engine = criar_engine(url)
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture
def db(engine) -> Iterator[Session]:
    """Sessão ligada ao banco de teste."""
    fabrica = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    sessao = fabrica()
    try:
        yield sessao
    finally:
        sessao.close()


@pytest.fixture
def client(
    db: Session, engine, monkeypatch: pytest.MonkeyPatch
) -> Iterator[TestClient]:
    """Cliente HTTP com o banco de teste injetado no lugar do real.

    A sessão de requisição usa `db` diretamente, mas a tarefa de background
    da simulação cria sua **própria** sessão via `SessionLocal()` — sem
    redirecioná-la para o engine de teste, ela escreveria no banco de
    desenvolvimento de verdade.
    """

    def _get_db_teste() -> Iterator[Session]:
        yield db

    fabrica_teste = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    monkeypatch.setattr("app.services.simulacao.executor.SessionLocal", fabrica_teste)

    app.dependency_overrides[get_db] = _get_db_teste
    with TestClient(app) as cliente:
        yield cliente
    app.dependency_overrides.clear()

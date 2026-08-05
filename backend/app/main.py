"""Aplicação FastAPI.

O sistema é **aberto**: não há autenticação, cadastro de usuários nem controle
de permissões — decisão explícita de produto.
"""

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import health
from app.core.config import settings
from app.db.migrations import aplicar_migracoes

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

DESCRICAO = """
Simulador de abertura de turmas a partir da disponibilidade dos instrutores.

As turmas são **saída** da simulação, não entrada: o sistema responde a partir de
que data cada tipologia pode ser aberta e com quais instrutores.

Sistema aberto — sem autenticação.
"""


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Prepara o banco antes de atender a primeira requisição."""
    settings.garantir_diretorios()
    aplicar_migracoes()
    yield


app = FastAPI(
    title=settings.app_nome,
    version=settings.app_versao,
    description=DESCRICAO,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)


@app.get("/", tags=["health"])
def raiz() -> dict[str, str]:
    """Ponto de entrada com atalho para a documentação."""
    return {
        "aplicacao": settings.app_nome,
        "versao": settings.app_versao,
        "docs": "/docs",
    }

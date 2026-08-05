"""Verificação de saúde da aplicação."""

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db

router = APIRouter(tags=["health"])


@router.get("/health")
def health(db: Session = Depends(get_db)) -> dict[str, object]:
    """Retorna o estado da aplicação e a conectividade com o banco."""
    try:
        db.execute(text("SELECT 1"))
        banco_ok = True
        erro_banco = None
    except Exception as exc:  # noqa: BLE001 - qualquer falha aqui é falha de saúde
        banco_ok = False
        erro_banco = str(exc)

    return {
        "status": "ok" if banco_ok else "degradado",
        "aplicacao": settings.app_nome,
        "versao": settings.app_versao,
        "banco": {
            "conectado": banco_ok,
            "erro": erro_banco,
        },
    }

"""Isolamento transacional por linha na importação.

Um `rollback()` comum desfaz **toda** a transação, descartando as linhas
válidas já processadas junto com a linha ruim — e o contador de importados
continuaria alto, produzindo perda silenciosa de dados.

O SAVEPOINT limita o descarte à linha que falhou.
"""

from collections.abc import Callable

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.services.importacao.campos import ValorInvalidoError
from app.services.importacao.leitor_planilha import Linha
from app.services.importacao.resultado import ResultadoImportacao


class Resultado:
    """Como uma linha terminou."""

    CRIADO = "criado"
    ATUALIZADO = "atualizado"


def processar_linhas(
    db: Session,
    linhas: list[Linha],
    processar: Callable[[Session, Linha], str],
    resultado: ResultadoImportacao,
) -> None:
    """Processa cada linha num SAVEPOINT próprio.

    `processar` devolve `Resultado.CRIADO` ou `Resultado.ATUALIZADO`. Os
    contadores só avançam depois que o SAVEPOINT é liberado com sucesso, de
    modo que nunca divirjam do que está de fato no banco.
    """
    for linha in linhas:
        try:
            with db.begin_nested():
                situacao = processar(db, linha)
        except ValorInvalidoError as exc:
            resultado.adicionar_erro(linha.numero, str(exc))
        except IntegrityError as exc:
            resultado.adicionar_erro(linha.numero, _mensagem_integridade(exc))
        else:
            if situacao == Resultado.CRIADO:
                resultado.importados += 1
            else:
                resultado.atualizados += 1

    db.commit()


def _mensagem_integridade(exc: IntegrityError) -> str:
    """Traduz a violação do banco em texto compreensível ao operador."""
    detalhe = str(getattr(exc, "orig", exc))

    if "UNIQUE constraint failed" in detalhe:
        return "Registro duplicado: já existe outro com o mesmo identificador"
    if "FOREIGN KEY constraint failed" in detalhe:
        return "Referência inválida: o registro relacionado não existe"
    if "CHECK constraint failed" in detalhe:
        return f"Valor fora do permitido pelas regras do sistema ({detalhe})"
    return f"Não foi possível gravar a linha: {detalhe}"

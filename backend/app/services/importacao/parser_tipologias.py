"""Importação da planilha de tipologias.

O catálogo já nasce da planilha de instrutores; esta importação apenas
**completa** a carga horária total e as horas por encontro, que a primeira não
traz. Enquanto faltarem, a tipologia fica pendente e bloqueia a simulação.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import InstrutorTipologia, Tipologia
from app.services.importacao.campos import ValorInvalidoError, parse_inteiro, parse_numero
from app.services.importacao.leitor_planilha import Linha, ler_planilha
from app.services.importacao.resultado import ArquivoInvalidoError, ResultadoImportacao
from app.services.importacao.transacao import Resultado, processar_linhas

COLUNAS_OBRIGATORIAS = ["tipologia", "carga_horaria_total", "horas_por_encontro"]

CARGA_TOTAL_MIN = 24
CARGA_TOTAL_MAX = 60


def importar_tipologias(db: Session, conteudo: bytes, nome_arquivo: str) -> ResultadoImportacao:
    """Configura a carga horária das tipologias do catálogo."""
    resultado = ResultadoImportacao()

    try:
        planilha = ler_planilha(conteudo, nome_arquivo)
        planilha.exigir_colunas(COLUNAS_OBRIGATORIAS)
    except ArquivoInvalidoError as exc:
        resultado.erro_arquivo = str(exc)
        return resultado

    nomes_processados: list[str] = []

    def processar(sessao: Session, linha: Linha) -> str:
        situacao, nome = _importar_linha(sessao, linha)
        nomes_processados.append(nome)
        return situacao

    processar_linhas(db, planilha.linhas, processar, resultado)
    _alertar_tipologias_orfas(db, nomes_processados, resultado)
    return resultado


def _importar_linha(db: Session, linha: Linha) -> tuple[str, str]:
    """Configura uma tipologia. Devolve a situação e o nome processado."""
    nome = linha.texto("tipologia")
    if not nome:
        raise ValorInvalidoError("Nome da tipologia não informado")

    carga_total = parse_inteiro(linha.texto("carga_horaria_total"), "Carga horária total")
    horas_encontro = parse_numero(linha.texto("horas_por_encontro"), "Horas por encontro")

    _validar_carga(carga_total, horas_encontro)

    tipologia = db.scalar(select(Tipologia).where(Tipologia.nome == nome))
    if tipologia is None:
        tipologia = Tipologia(nome=nome)
        db.add(tipologia)
        situacao = Resultado.CRIADO
    else:
        situacao = Resultado.ATUALIZADO

    tipologia.carga_horaria_total_horas = carga_total
    tipologia.horas_por_encontro = horas_encontro
    tipologia.descricao = linha.texto("descricao") or tipologia.descricao

    db.flush()
    return situacao, nome


def _alertar_tipologias_orfas(
    db: Session, nomes: list[str], resultado: ResultadoImportacao
) -> None:
    """Avisa sobre tipologias que nenhum instrutor domina.

    Aceitas de propósito: o dado está correto, apenas nunca gerará oferta.
    Calculado após o commit, para não alertar sobre linha que acabou rejeitada.
    """
    orfas = [
        nome
        for nome in nomes
        if (t := db.scalar(select(Tipologia).where(Tipologia.nome == nome)))
        and not _tem_instrutor(db, t.id)
    ]
    for nome in orfas:
        resultado.adicionar_alerta(
            f"Tipologia '{nome}' não é dominada por nenhum instrutor — "
            "nunca será ofertada nas simulações."
        )


def _validar_carga(carga_total: int, horas_encontro: float) -> None:
    if horas_encontro <= 0:
        raise ValorInvalidoError("Horas por encontro deve ser maior que zero")

    if not CARGA_TOTAL_MIN <= carga_total <= CARGA_TOTAL_MAX:
        raise ValorInvalidoError(
            f"Carga horária total fora da faixa: {carga_total}h. "
            f"Aceito de {CARGA_TOTAL_MIN}h a {CARGA_TOTAL_MAX}h"
        )

    # Sem divisão exata o número de encontros não fecha em valor inteiro, e a
    # turma terminaria com carga horária diferente da prevista.
    encontros = carga_total / horas_encontro
    if encontros != int(encontros):
        raise ValorInvalidoError(
            f"Carga horária total ({carga_total}h) não é múltiplo exato das horas "
            f"por encontro ({horas_encontro}h): resultaria em {encontros:.2f} encontros"
        )


def _tem_instrutor(db: Session, tipologia_id: int) -> bool:
    vinculo = db.scalar(
        select(InstrutorTipologia).where(InstrutorTipologia.tipologia_id == tipologia_id).limit(1)
    )
    return vinculo is not None


def listar_pendentes(db: Session) -> list[Tipologia]:
    """Tipologias sem carga horária configurada, que bloqueiam a simulação."""
    return [t for t in db.scalars(select(Tipologia).order_by(Tipologia.nome)).all()
            if not t.configurada]

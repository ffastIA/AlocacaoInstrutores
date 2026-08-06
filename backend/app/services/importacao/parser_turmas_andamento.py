"""Importação da planilha de turmas em andamento.

Retrata a situação atual das alocações. Estas turmas não são decisão do
solver: consomem capacidade do instrutor até sua data de término, e é isso que
torna a disponibilidade progressiva ao longo do período simulado.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Instrutor, Modalidade, Tipologia, TurmaEmAndamento, Turno
from app.services.importacao.campos import ValorInvalidoError, parse_data, parse_turno
from app.services.importacao.leitor_planilha import Linha, ler_planilha, normalizar_cabecalho
from app.services.importacao.resultado import ArquivoInvalidoError, ResultadoImportacao
from app.services.importacao.transacao import Resultado, processar_linhas

COLUNAS_OBRIGATORIAS = [
    "instrutor",
    "tipologia",
    "modalidade",
    "turno",
    "data_inicio",
    "data_fim_prevista",
]


def importar_turmas_andamento(
    db: Session, conteudo: bytes, nome_arquivo: str
) -> ResultadoImportacao:
    """Importa a situação atual. Planilha vazia é cenário válido — campo livre."""
    resultado = ResultadoImportacao()

    try:
        planilha = ler_planilha(conteudo, nome_arquivo)
        planilha.exigir_colunas(COLUNAS_OBRIGATORIAS)
    except ArquivoInvalidoError as exc:
        resultado.erro_arquivo = str(exc)
        return resultado

    processar_linhas(db, planilha.linhas, _importar_linha, resultado)
    _alertar_sobreposicao_de_slot(db, resultado)
    return resultado


def _importar_linha(db: Session, linha: Linha) -> str:
    instrutor = _resolver_instrutor(db, linha.texto("instrutor"))
    tipologia = _resolver_tipologia(db, linha.texto("tipologia"))
    modalidade = _parse_modalidade(linha.texto("modalidade"))
    turno = parse_turno(linha.texto("turno"))

    _validar_turno_do_instrutor(instrutor, turno)

    data_inicio = parse_data(linha.texto("data_inicio"), "Data de início")
    data_fim = parse_data(linha.texto("data_fim_prevista"), "Data de término prevista")
    if data_fim < data_inicio:
        raise ValorInvalidoError(
            f"Data de término ({data_fim:%d/%m/%Y}) é anterior à de início ({data_inicio:%d/%m/%Y})"
        )

    db.add(
        TurmaEmAndamento(
            codigo_turma=linha.texto("codigo_turma") or None,
            instrutor_id=instrutor.id,
            tipologia_id=tipologia.id,
            projeto_id=instrutor.projeto_id,
            modalidade=modalidade,
            turno=turno,
            data_inicio=data_inicio,
            data_fim_prevista=data_fim,
        )
    )
    db.flush()
    return Resultado.CRIADO


def _resolver_instrutor(db: Session, nome: str) -> Instrutor:
    if not nome:
        raise ValorInvalidoError("Instrutor não informado")
    instrutor = db.scalar(select(Instrutor).where(Instrutor.nome == nome))
    if instrutor is None:
        raise ValorInvalidoError(
            f"Instrutor não encontrado: '{nome}'. "
            "Importe a planilha de instrutores antes das turmas em andamento"
        )
    return instrutor


def _resolver_tipologia(db: Session, nome: str) -> Tipologia:
    if not nome:
        raise ValorInvalidoError("Tipologia não informada")
    tipologia = db.scalar(select(Tipologia).where(Tipologia.nome == nome))
    if tipologia is None:
        raise ValorInvalidoError(f"Tipologia não encontrada no catálogo: '{nome}'")
    return tipologia


def _parse_modalidade(texto: str) -> Modalidade:
    if not texto:
        raise ValorInvalidoError("Modalidade não informada")
    try:
        return Modalidade(normalizar_cabecalho(texto))
    except ValueError:
        validas = ", ".join(m.value for m in Modalidade)
        raise ValorInvalidoError(
            f"Modalidade inválida: '{texto}'. Valores aceitos: {validas}"
        ) from None


def _validar_turno_do_instrutor(instrutor: Instrutor, turno: Turno) -> None:
    disponiveis = {t.turno for t in instrutor.turnos}
    if turno not in disponiveis:
        nomes = ", ".join(sorted(t.value for t in disponiveis)) or "(nenhum)"
        raise ValorInvalidoError(
            f"Instrutor '{instrutor.nome}' não está disponível no turno "
            f"'{turno.value}'. Turnos disponíveis: {nomes}"
        )


def _alertar_sobreposicao_de_slot(db: Session, resultado: ResultadoImportacao) -> None:
    """Sinaliza turmas do mesmo instrutor no mesmo slot com períodos sobrepostos.

    Cada slot comporta no máximo uma turma por vez, mas isso é aceito de
    propósito na importação — é o retrato do mundo real, não um erro de
    preenchimento. Recusar impediria a equipe de simular exatamente o caso em
    que mais precisa de ajuda.
    """
    turmas = db.scalars(select(TurmaEmAndamento)).all()

    por_slot: dict[tuple[int, Turno], list[TurmaEmAndamento]] = {}
    for turma in turmas:
        chave = (turma.instrutor_id, turma.turno)
        por_slot.setdefault(chave, []).append(turma)

    for (instrutor_id, turno), grupo in sorted(por_slot.items(), key=lambda x: x[0][0]):
        if len(grupo) < 2:
            continue
        instrutor = db.get(Instrutor, instrutor_id)
        if instrutor is None:
            continue
        grupo_ordenado = sorted(grupo, key=lambda t: t.data_inicio)
        for anterior, atual in zip(grupo_ordenado, grupo_ordenado[1:], strict=False):
            if atual.data_inicio <= anterior.data_fim_prevista:
                resultado.adicionar_alerta(
                    f"Instrutor '{instrutor.nome}' tem turmas em andamento com períodos "
                    f"sobrepostos no slot '{turno.value}' — apenas uma turma pode ocupar o "
                    "slot por vez."
                )
                break

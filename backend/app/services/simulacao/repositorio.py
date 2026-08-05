"""Conversão dos dados de domínio (SQLAlchemy) para as dataclasses puras do motor.

O motor (`app.services.solver`) é independente de banco por design — este
módulo é a única ponte entre os dois mundos.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Instrutor, Tipologia, TurmaEmAndamento
from app.services.solver.dados import InstrutorDados, TipologiaDados, TurmaAndamentoDados


def carregar_instrutores(db: Session, projeto_ids: list[int] | None) -> list[InstrutorDados]:
    """Carrega instrutores ativos, opcionalmente filtrados por projeto.

    `projeto_ids` None ou vazio significa todos os projetos — usado quando o
    compartilhamento entre projetos está ligado, ou quando o cenário não
    restringe o escopo.
    """
    consulta = select(Instrutor).where(Instrutor.ativo.is_(True))
    if projeto_ids:
        consulta = consulta.where(Instrutor.projeto_id.in_(projeto_ids))

    return [
        InstrutorDados(
            id=i.id,
            projeto_id=i.projeto_id,
            turnos={t.turno: t.carga_horaria_horas for t in i.turnos},
            dias_semana=frozenset(d.dia_semana for d in i.dias),
            tipologia_ids=frozenset(v.tipologia_id for v in i.tipologias),
        )
        for i in db.scalars(consulta).all()
    ]


def carregar_tipologias_configuradas(db: Session) -> dict[int, TipologiaDados]:
    """Tipologias com carga horária definida — as únicas que podem gerar candidatas."""
    return {
        t.id: TipologiaDados(
            id=t.id,
            carga_horaria_total_horas=t.carga_horaria_total_horas,
            horas_por_encontro=t.horas_por_encontro,
        )
        for t in db.scalars(select(Tipologia)).all()
        if t.configurada
    }


def listar_tipologias_pendentes_no_escopo(
    db: Session, instrutores: list[InstrutorDados]
) -> list[str]:
    """Nomes das tipologias que instrutores do escopo dominam mas ainda não
    têm carga horária configurada — cada uma bloqueia a execução."""
    ids_dominados = {tid for i in instrutores for tid in i.tipologia_ids}
    if not ids_dominados:
        return []
    tipologias = db.scalars(select(Tipologia).where(Tipologia.id.in_(ids_dominados))).all()
    return sorted(t.nome for t in tipologias if not t.configurada)


def carregar_turmas_andamento(
    db: Session, instrutor_ids: set[int]
) -> list[TurmaAndamentoDados]:
    if not instrutor_ids:
        return []
    consulta = select(TurmaEmAndamento).where(TurmaEmAndamento.instrutor_id.in_(instrutor_ids))
    return [
        TurmaAndamentoDados(
            instrutor_id=t.instrutor_id,
            tipologia_id=t.tipologia_id,
            modalidade=t.modalidade,
            turno=t.turno,
            data_inicio=t.data_inicio,
            data_fim_prevista=t.data_fim_prevista,
        )
        for t in db.scalars(consulta).all()
    ]

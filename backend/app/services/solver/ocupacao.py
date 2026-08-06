"""Ocupação de capacidade derivada das turmas em andamento.

Turmas em andamento não são decisão do solver — são fatos fixos, usados para
saber quais (instrutor, slot, data) já estão ocupados e quantos slot-dias cada
instrutor já tem consumidos. É esse cálculo que alimenta tanto a poda do
gerador de candidatas quanto as restrições do CP-SAT.

Cada slot de turno comporta no máximo uma turma por vez — ocupação binária,
sem conceito de horas ou carga horária declarada por turno.
"""

from dataclasses import dataclass
from datetime import date, timedelta

from app.models.enums import Turno
from app.services.solver.dados import (
    InstrutorDados,
    TurmaAndamentoDados,
    dia_planilha_para_isoweekday,
)


@dataclass(frozen=True)
class Ocupacao:
    slots_ocupados: frozenset[tuple[int, Turno, date]]


def calcular_ocupacao(turmas_andamento: list[TurmaAndamentoDados]) -> Ocupacao:
    """Reconstrói o calendário de cada turma em andamento e marca os slots ocupados."""
    slots: set[tuple[int, Turno, date]] = set()

    for turma in turmas_andamento:
        dias_iso = {dia_planilha_para_isoweekday(d) for d in turma.modalidade.dias_semana}

        data_atual = turma.data_inicio
        while data_atual <= turma.data_fim_prevista:
            if data_atual.isoweekday() in dias_iso:
                slots.add((turma.instrutor_id, turma.turno, data_atual))
            data_atual += timedelta(days=1)

    return Ocupacao(slots_ocupados=frozenset(slots))


def slots_ocupados_total(
    ocupacao: Ocupacao, instrutor_id: int, periodo_de: date, periodo_ate: date
) -> int:
    """Conta quantos slot-dias do instrutor já estão ocupados, dentro do período."""
    return sum(
        1
        for (iid, _turno, data) in ocupacao.slots_ocupados
        if iid == instrutor_id and periodo_de <= data <= periodo_ate
    )


def dias_uteis_no_periodo(
    dias_semana_planilha: frozenset[int], periodo_de: date, periodo_ate: date
) -> int:
    """Conta os dias do período que casam com os dias disponíveis do instrutor.

    Restrito a segunda-quinta: o dia 6 (sexta) nunca conta como capacidade
    regular, apenas como reposição.
    """
    dias_iso_validos = {
        dia_planilha_para_isoweekday(d) for d in dias_semana_planilha if d != 6
    }
    contagem = 0
    data_atual = periodo_de
    while data_atual <= periodo_ate:
        if data_atual.isoweekday() in dias_iso_validos:
            contagem += 1
        data_atual += timedelta(days=1)
    return contagem


def slots_disponiveis_periodo(
    instrutor: InstrutorDados, periodo_de: date, periodo_ate: date
) -> int:
    """Quantidade de slot-dias disponíveis do instrutor ao longo do período simulado."""
    dias = dias_uteis_no_periodo(instrutor.dias_semana, periodo_de, periodo_ate)
    return len(instrutor.turnos) * dias

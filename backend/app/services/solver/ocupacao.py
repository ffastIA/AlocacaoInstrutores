"""Ocupação de capacidade derivada das turmas em andamento.

Turmas em andamento não são decisão do solver — são fatos fixos, usados para
calcular quanto de capacidade já está consumida em cada (instrutor, turno,
data) e quantas turmas cada instrutor já tem em cada dia. É esse cálculo que
alimenta tanto a poda do gerador de candidatas quanto as restrições do CP-SAT.
"""

from dataclasses import dataclass
from datetime import date, timedelta

from app.models.enums import Turno
from app.services.solver.dados import (
    InstrutorDados,
    TipologiaDados,
    TurmaAndamentoDados,
    dia_planilha_para_isoweekday,
)


@dataclass(frozen=True)
class Ocupacao:
    horas_por_turno_data: dict[tuple[int, Turno, date], float]
    turmas_por_data: dict[tuple[int, date], int]


def calcular_ocupacao(
    turmas_andamento: list[TurmaAndamentoDados],
    tipologias: dict[int, TipologiaDados],
) -> Ocupacao:
    """Reconstrói o calendário de cada turma em andamento e agrega a ocupação.

    Sem carga horária configurada para a tipologia, assume-se o turno inteiro
    ocupado (`float("inf")`) — mais seguro do que subestimar a ocupação real.
    """
    horas: dict[tuple[int, Turno, date], float] = {}
    contagem: dict[tuple[int, date], int] = {}

    for turma in turmas_andamento:
        tipologia = tipologias.get(turma.tipologia_id)
        horas_encontro = tipologia.horas_por_encontro if tipologia else float("inf")
        dias_iso = {dia_planilha_para_isoweekday(d) for d in turma.modalidade.dias_semana}

        data_atual = turma.data_inicio
        while data_atual <= turma.data_fim_prevista:
            if data_atual.isoweekday() in dias_iso:
                chave_turno = (turma.instrutor_id, turma.turno, data_atual)
                horas[chave_turno] = horas.get(chave_turno, 0.0) + horas_encontro

                chave_dia = (turma.instrutor_id, data_atual)
                contagem[chave_dia] = contagem.get(chave_dia, 0) + 1
            data_atual += timedelta(days=1)

    return Ocupacao(horas_por_turno_data=horas, turmas_por_data=contagem)


def ocupado_fixo_total(ocupacao: Ocupacao, instrutor_id: int) -> float:
    """Soma as horas fixas ocupadas de um instrutor, em qualquer turno/data.

    Retorna infinito se alguma turma em andamento tiver tipologia sem carga
    horária configurada (ocupação desconhecida, tratada como pior caso).
    """
    total = 0.0
    for (iid, _turno, _data), horas_valor in ocupacao.horas_por_turno_data.items():
        if iid != instrutor_id:
            continue
        if horas_valor == float("inf"):
            return float("inf")
        total += horas_valor
    return total


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


def horas_disponiveis_periodo(
    instrutor: InstrutorDados, periodo_de: date, periodo_ate: date
) -> float:
    """Capacidade horária total do instrutor ao longo do período simulado."""
    dias = dias_uteis_no_periodo(instrutor.dias_semana, periodo_de, periodo_ate)
    return sum(capacidade * dias for capacidade in instrutor.turnos.values())

"""Estruturas de dados de entrada do motor de simulação.

Módulo neutro (sem depender de `gerador_candidatas` nem de `ocupacao`) — os
dois importam daqui, evitando import circular entre eles.

Dataclasses próprias, independentes de SQLAlchemy: permitem validar o motor
com dados sintéticos, sem depender de banco.
"""

from dataclasses import dataclass
from datetime import date

from app.models.enums import Modalidade, Turno


@dataclass(frozen=True)
class InstrutorDados:
    id: int
    projeto_id: int
    turnos: frozenset[Turno]  # slots disponíveis; cada um comporta 1 turma por vez
    dias_semana: frozenset[int]  # numeração da planilha: 2=segunda ... 6=sexta
    tipologia_ids: frozenset[int]


@dataclass(frozen=True)
class TipologiaDados:
    id: int
    carga_horaria_total_horas: float
    horas_por_encontro: float


@dataclass(frozen=True)
class TurmaAndamentoDados:
    """Turma já em execução — consome capacidade, não é decisão do solver."""

    instrutor_id: int
    tipologia_id: int
    modalidade: Modalidade
    turno: Turno
    data_inicio: date
    data_fim_prevista: date


def dia_planilha_para_isoweekday(dia_planilha: int) -> int:
    """Converte a numeração da planilha (2=segunda...6=sexta) para ISO (1=segunda...5=sexta)."""
    return dia_planilha - 1

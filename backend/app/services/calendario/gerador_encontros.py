"""Geração determinística do calendário de encontros de uma turma.

Como turno e modalidade são fixos por candidata, o calendário fica totalmente
determinado assim que a semana de início é escolhida — não é uma variável de
decisão do solver, é um dado pré-computado.

Nenhum padrão de dias inclui sexta-feira: o dia é reservado a atividades
extraclasse e reposição, invariante de geração, não restrição do CP-SAT.
"""

from dataclasses import dataclass
from datetime import date, timedelta

from app.models.enums import Modalidade, Turno

# `Modalidade.dias_semana` usa a numeração da PLANILHA (2=segunda...6=sexta),
# diferente da numeração ISO usada por `date.isoweekday()` (1=segunda...5=sexta).
# A conversão entre as duas é a diferença abaixo — sem ela, cada dia desliza
# uma posição (quinta planilha vira sexta ISO).
_DIA_PLANILHA_SEGUNDA = 2


@dataclass(frozen=True)
class Encontro:
    data: date
    turno: Turno
    horas: float


@dataclass(frozen=True)
class CalendarioTurma:
    """Calendário completo de uma turma candidata."""

    encontros: tuple[Encontro, ...]

    @property
    def data_inicio(self) -> date:
        return self.encontros[0].data

    @property
    def data_fim(self) -> date:
        return self.encontros[-1].data

    @property
    def num_encontros(self) -> int:
        return len(self.encontros)

    @property
    def carga_horaria_total(self) -> float:
        return sum(e.horas for e in self.encontros)

    @property
    def datas(self) -> frozenset[date]:
        return frozenset(e.data for e in self.encontros)

    def horas_por_semana(self, segunda_semana_0: date) -> dict[int, float]:
        """Soma de horas por semana, indexada pelo deslocamento em relação à
        segunda-feira de referência. Semanas de borda somam menos que as
        cheias quando a turma inicia ou termina no meio da semana."""
        resultado: dict[int, float] = {}
        for encontro in self.encontros:
            semana = (encontro.data - segunda_semana_0).days // 7
            resultado[semana] = resultado.get(semana, 0.0) + encontro.horas
        return resultado


def segunda_feira_da_semana(data_referencia: date, deslocamento_semanas: int) -> date:
    """Segunda-feira que começa `deslocamento_semanas` após a semana de `data_referencia`."""
    segunda_da_referencia = data_referencia - timedelta(days=data_referencia.isoweekday() - 1)
    return segunda_da_referencia + timedelta(weeks=deslocamento_semanas)


def gerar_calendario(
    *,
    data_referencia: date,
    semana_inicio: int,
    modalidade: Modalidade,
    turno: Turno,
    carga_horaria_total_horas: float,
    horas_por_encontro: float,
) -> CalendarioTurma:
    """Gera o calendário de uma turma candidata.

    `semana_inicio` é o deslocamento em semanas a partir de `data_referencia`
    (semana 0 = a semana da própria data de referência).
    """
    num_encontros = _num_encontros(carga_horaria_total_horas, horas_por_encontro)
    dias_planilha = modalidade.dias_semana  # 2=segunda ... 5=quinta; nunca 6=sexta

    segunda = segunda_feira_da_semana(data_referencia, semana_inicio)

    encontros: list[Encontro] = []
    semana_atual = 0
    while len(encontros) < num_encontros:
        for dia_planilha in dias_planilha:
            if len(encontros) >= num_encontros:
                break
            deslocamento_dias = dia_planilha - _DIA_PLANILHA_SEGUNDA
            data_encontro = segunda + timedelta(weeks=semana_atual, days=deslocamento_dias)
            encontros.append(Encontro(data=data_encontro, turno=turno, horas=horas_por_encontro))
        semana_atual += 1

    return CalendarioTurma(encontros=tuple(encontros))


def _num_encontros(carga_total: float, horas_por_encontro: float) -> int:
    bruto = carga_total / horas_por_encontro
    arredondado = round(bruto)
    # Tolerância a erro de ponto flutuante (ex.: 60/3 podendo dar 19.999999999997).
    if abs(bruto - arredondado) > 1e-6:
        raise ValueError(
            f"Carga horária total ({carga_total}h) não é múltiplo exato das horas "
            f"por encontro ({horas_por_encontro}h)"
        )
    return arredondado


def duracao_em_semanas(modalidade: Modalidade, num_encontros: int) -> int:
    """Quantidade de semanas (cheias ou parciais) que a turma ocupa.

    Usado para dimensionar as semanas de início candidatas sem gerar o
    calendário completo — cálculo puramente aritmético, mais barato.
    """
    encontros_por_semana = len(modalidade.dias_semana)
    semanas_completas, resto = divmod(num_encontros, encontros_por_semana)
    return semanas_completas + (1 if resto else 0)

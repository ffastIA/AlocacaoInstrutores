"""Enumerações do domínio.

Todas herdam de `str` para serializar diretamente em JSON e para que o valor
gravado no banco seja legível.
"""

from enum import StrEnum


class Turno(StrEnum):
    MANHA = "manha"
    TARDE = "tarde"
    NOITE = "noite"


class Modalidade(StrEnum):
    """Padrão de dias de uma turma.

    Nenhuma modalidade inclui sexta-feira: o dia é reservado a atividades
    extraclasse e reposição.
    """

    REGULAR_SEG_QUA = "regular_seg_qua"
    REGULAR_TER_QUI = "regular_ter_qui"
    INTENSIVA_SEG_QUI = "intensiva_seg_qui"

    @property
    def dias_semana(self) -> tuple[int, ...]:
        """Dias da semana no padrão da planilha: 2 = segunda ... 6 = sexta."""
        return _DIAS_POR_MODALIDADE[self]


_DIAS_POR_MODALIDADE: dict[Modalidade, tuple[int, ...]] = {
    Modalidade.REGULAR_SEG_QUA: (2, 4),
    Modalidade.REGULAR_TER_QUI: (3, 5),
    Modalidade.INTENSIVA_SEG_QUI: (2, 3, 4, 5),
}


class TipoDataNaoLetiva(StrEnum):
    FERIADO = "feriado"
    RECESSO = "recesso"
    FERIAS = "ferias"


class StatusSimulacao(StrEnum):
    PENDENTE = "pendente"
    EXECUTANDO = "executando"
    CONCLUIDA = "concluida"
    ERRO = "erro"


class StatusTurma(StrEnum):
    EM_ANDAMENTO = "em_andamento"
    CONCLUIDA = "concluida"


# Dia da semana reservado a reposição, nunca alocado a turma regular.
DIA_REPOSICAO = 6

# Faixa de dias aceita na disponibilidade do instrutor: segunda a sexta.
DIA_SEMANA_MIN = 2
DIA_SEMANA_MAX = 6

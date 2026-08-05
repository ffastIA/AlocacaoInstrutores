"""Modelos e enums do domínio.

Importar tudo aqui garante que o Alembic enxergue todas as tabelas ao ler os
metadados da `Base`.
"""

from app.models.enums import (
    DIA_REPOSICAO,
    DIA_SEMANA_MAX,
    DIA_SEMANA_MIN,
    Modalidade,
    StatusSimulacao,
    StatusTurma,
    TipoDataNaoLetiva,
    Turno,
)
from app.models.models import (
    Cenario,
    CenarioProjeto,
    DataNaoLetiva,
    Instrutor,
    InstrutorDia,
    InstrutorTipologia,
    InstrutorTurno,
    OportunidadeSimulacao,
    Projeto,
    ResultadoKpis,
    Simulacao,
    SnapshotCapacidade,
    Tipologia,
    TurmaEmAndamento,
    TurmaSugerida,
    TurmaSugeridaEncontro,
)

__all__ = [
    "DIA_REPOSICAO",
    "DIA_SEMANA_MAX",
    "DIA_SEMANA_MIN",
    "Cenario",
    "CenarioProjeto",
    "DataNaoLetiva",
    "Instrutor",
    "InstrutorDia",
    "InstrutorTipologia",
    "InstrutorTurno",
    "Modalidade",
    "OportunidadeSimulacao",
    "Projeto",
    "ResultadoKpis",
    "Simulacao",
    "SnapshotCapacidade",
    "StatusSimulacao",
    "StatusTurma",
    "TipoDataNaoLetiva",
    "Tipologia",
    "TurmaEmAndamento",
    "TurmaSugerida",
    "TurmaSugeridaEncontro",
    "Turno",
]

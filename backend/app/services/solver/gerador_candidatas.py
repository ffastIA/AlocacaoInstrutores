"""Enumeração das turmas candidatas.

Uma candidata é a combinação (instrutor, tipologia, turno, modalidade, semana
de início). Como o calendário de cada uma é determinístico (ver
`gerador_encontros`), a única decisão do solver é "abrir ou não" — não há
necessidade de o CP-SAT decidir datas.

A poda acontece **aqui**, não como restrição do solver: uma combinação
inelegível (tipologia não dominada, turno indisponível, dias incompatíveis,
horas por encontro acima da capacidade do turno, turma que não cabe no
período, ou que colide sozinha com uma turma em andamento) simplesmente não
gera variável — reduzindo o modelo antes de o solver começar.
"""

from dataclasses import dataclass
from datetime import date

from app.models.enums import Modalidade, Turno
from app.services.calendario.gerador_encontros import (
    CalendarioTurma,
    gerar_calendario,
    segunda_feira_da_semana,
)
from app.services.solver.dados import InstrutorDados, TipologiaDados, TurmaAndamentoDados
from app.services.solver.ocupacao import Ocupacao, calcular_ocupacao

__all__ = [
    "Candidata",
    "InstrutorDados",
    "TipologiaDados",
    "TurmaAndamentoDados",
    "gerar_candidatas",
]


@dataclass(frozen=True)
class CandidataSemId:
    """Candidata antes da numeração final — uso interno da enumeração."""

    instrutor_id: int
    tipologia_id: int
    projeto_id: int
    turno: Turno
    modalidade: Modalidade
    semana_inicio: int
    calendario: CalendarioTurma


@dataclass(frozen=True)
class Candidata:
    """Uma turma candidata pronta para virar variável de decisão no solver."""

    id: int  # índice sequencial, chave da variável z[c]
    instrutor_id: int
    tipologia_id: int
    projeto_id: int
    turno: Turno
    modalidade: Modalidade
    semana_inicio: int
    calendario: CalendarioTurma


def gerar_candidatas(
    *,
    instrutores: list[InstrutorDados],
    tipologias: dict[int, TipologiaDados],
    turmas_andamento: list[TurmaAndamentoDados],
    periodo_de: date,
    periodo_ate: date,
    projetos_escopo: frozenset[int],
    permitir_compartilhamento: bool,
) -> list[Candidata]:
    """Enumera as candidatas elegíveis no período e escopo informados.

    `projetos_escopo` vazio, ou `permitir_compartilhamento=True`, significa
    "todos os projetos" — quando ligado, o pool de instrutores é único e o
    escopo deixa de restringir quem pode gerar candidatas.
    """
    ocupacao = calcular_ocupacao(turmas_andamento, tipologias)
    projetos_permitidos = (
        None if (permitir_compartilhamento or not projetos_escopo) else projetos_escopo
    )

    candidatas: list[CandidataSemId] = []

    for instrutor in instrutores:
        if projetos_permitidos is not None and instrutor.projeto_id not in projetos_permitidos:
            continue

        for tipologia_id in sorted(instrutor.tipologia_ids):
            tipologia = tipologias.get(tipologia_id)
            if tipologia is None:
                # Tipologia pendente de configuração: nunca gera candidata.
                continue

            for turno in sorted(instrutor.turnos):
                capacidade_turno = instrutor.turnos[turno]
                if tipologia.horas_por_encontro > capacidade_turno:
                    continue

                for modalidade in Modalidade:
                    if not set(modalidade.dias_semana) <= instrutor.dias_semana:
                        continue

                    candidatas.extend(
                        _candidatas_da_combinacao(
                            instrutor=instrutor,
                            tipologia=tipologia,
                            turno=turno,
                            capacidade_turno=capacidade_turno,
                            modalidade=modalidade,
                            periodo_de=periodo_de,
                            periodo_ate=periodo_ate,
                            ocupacao=ocupacao,
                        )
                    )

    return [
        Candidata(
            id=indice,
            instrutor_id=c.instrutor_id,
            tipologia_id=c.tipologia_id,
            projeto_id=c.projeto_id,
            turno=c.turno,
            modalidade=c.modalidade,
            semana_inicio=c.semana_inicio,
            calendario=c.calendario,
        )
        for indice, c in enumerate(candidatas)
    ]


def _candidatas_da_combinacao(
    *,
    instrutor: InstrutorDados,
    tipologia: TipologiaDados,
    turno: Turno,
    capacidade_turno: float,
    modalidade: Modalidade,
    periodo_de: date,
    periodo_ate: date,
    ocupacao: Ocupacao,
) -> list[CandidataSemId]:
    """Gera as candidatas de uma combinação fixa, variando a semana de início."""
    resultado: list[CandidataSemId] = []
    semana = 0

    while segunda_feira_da_semana(periodo_de, semana) <= periodo_ate:
        calendario = gerar_calendario(
            data_referencia=periodo_de,
            semana_inicio=semana,
            modalidade=modalidade,
            turno=turno,
            carga_horaria_total_horas=tipologia.carga_horaria_total_horas,
            horas_por_encontro=tipologia.horas_por_encontro,
        )

        cabe_no_periodo = (
            calendario.data_inicio >= periodo_de and calendario.data_fim <= periodo_ate
        )
        if cabe_no_periodo and _cabe_na_capacidade_livre(
            calendario, instrutor.id, turno, capacidade_turno, ocupacao
        ):
            resultado.append(
                CandidataSemId(
                    instrutor_id=instrutor.id,
                    tipologia_id=tipologia.id,
                    projeto_id=instrutor.projeto_id,
                    turno=turno,
                    modalidade=modalidade,
                    semana_inicio=semana,
                    calendario=calendario,
                )
            )

        semana += 1

    return resultado


def _cabe_na_capacidade_livre(
    calendario: CalendarioTurma,
    instrutor_id: int,
    turno: Turno,
    capacidade_turno: float,
    ocupacao: Ocupacao,
) -> bool:
    """A candidata, sozinha, respeita a capacidade já ocupada por turmas em andamento.

    Não elimina conflitos entre candidatas concorrentes — isso permanece como
    restrição genuína do solver (duas candidatas podem caber cada uma
    isoladamente, mas não juntas).
    """
    for encontro in calendario.encontros:
        ocupado = ocupacao.horas_por_turno_data.get((instrutor_id, turno, encontro.data), 0.0)
        if ocupado + encontro.horas > capacidade_turno:
            return False
    return True

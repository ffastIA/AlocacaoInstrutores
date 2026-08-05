"""Indicadores de resultado de uma simulação.

Calculados a partir das candidatas selecionadas pelo solver, das turmas em
andamento e dos dados de instrutores — sem depender do modelo CP-SAT em si.
"""

from dataclasses import dataclass
from datetime import date, timedelta

from app.models.enums import DIA_REPOSICAO, Turno
from app.services.solver.cp_sat_model import ResultadoSolver
from app.services.solver.dados import InstrutorDados, TurmaAndamentoDados
from app.services.solver.gerador_candidatas import Candidata
from app.services.solver.ocupacao import (
    Ocupacao,
    calcular_ocupacao,
    dias_uteis_no_periodo,
    ocupado_fixo_total,
)


@dataclass(frozen=True)
class UtilizacaoInstrutor:
    instrutor_id: int
    horas_alocadas: float
    horas_disponiveis: float

    @property
    def utilizacao_percentual(self) -> float:
        if self.horas_disponiveis <= 0:
            return 0.0
        return min(self.horas_alocadas / self.horas_disponiveis, 1.0) * 100


@dataclass(frozen=True)
class OportunidadeTipologia:
    """A partir de quando uma tipologia pode ser aberta, e com quais instrutores."""

    tipologia_id: int
    data_inicio: date
    instrutor_ids: tuple[int, ...]
    total_turmas: int


@dataclass(frozen=True)
class MetadadosExecucao:
    total_turmas_sugeridas: int
    horas_formacao_total: float
    objetivo_valor: float | None
    status_solver: str
    tempo_execucao_seg: float


@dataclass(frozen=True)
class ResultadoMetricas:
    pct_ociosidade: float
    utilizacao_por_instrutor: tuple[UtilizacaoInstrutor, ...]
    indice_balanceamento_carga: float
    distribuicao_por_tipologia: dict[int, int]
    indice_balanceamento_tipologias: float
    primeira_data_livre: dict[int, date]
    oportunidades: tuple[OportunidadeTipologia, ...]
    horas_reposicao_sexta: float
    metadados: MetadadosExecucao


def calcular_metricas(
    *,
    resultado_solver: ResultadoSolver,
    candidatas_geradas: list[Candidata],
    instrutores: list[InstrutorDados],
    turmas_andamento: list[TurmaAndamentoDados],
    periodo_de: date,
    periodo_ate: date,
) -> ResultadoMetricas:
    """Calcula os indicadores de uma simulação já resolvida.

    `candidatas_geradas` é o universo completo enumerado (não só as
    selecionadas) — necessário para o leque de tipologias possíveis e para o
    diagnóstico de capacidade.
    """
    selecionadas = resultado_solver.candidatas_selecionadas
    ocupacao = calcular_ocupacao(turmas_andamento, {})

    utilizacoes = _calcular_utilizacao_por_instrutor(
        instrutores, selecionadas, ocupacao, periodo_de, periodo_ate
    )

    horas_alocadas_total = sum(u.horas_alocadas for u in utilizacoes)
    horas_disponiveis_total = sum(u.horas_disponiveis for u in utilizacoes)
    pct_ociosidade = (
        (1 - horas_alocadas_total / horas_disponiveis_total) * 100
        if horas_disponiveis_total > 0
        else 0.0
    )

    utilizacoes_validas = [u.utilizacao_percentual for u in utilizacoes if u.horas_disponiveis > 0]
    indice_balanceamento_carga = (
        max(utilizacoes_validas) - min(utilizacoes_validas) if utilizacoes_validas else 0.0
    )

    # Inclui toda tipologia com ao menos uma candidata gerada (universo
    # ofertável), com 0 como padrão. Sem isso, uma tipologia totalmente
    # excluída da seleção some do dicionário em vez de contar como 0 — e o
    # índice de desequilíbrio reportaria erroneamente "equilíbrio perfeito"
    # quando na verdade uma tipologia inteira ficou de fora.
    universo_tipologias = {c.tipologia_id for c in candidatas_geradas}
    distribuicao_tipologia = _distribuicao_por_tipologia(selecionadas, universo_tipologias)
    indice_balanceamento_tipologias = (
        max(distribuicao_tipologia.values()) - min(distribuicao_tipologia.values())
        if len(distribuicao_tipologia) >= 2
        else 0.0
    )

    primeira_data_livre = _primeira_data_livre_por_instrutor(
        instrutores, turmas_andamento, periodo_de
    )

    oportunidades = _leque_de_oportunidades(candidatas_geradas)

    horas_reposicao = _horas_reposicao_sexta(instrutores, periodo_de, periodo_ate)

    metadados = MetadadosExecucao(
        total_turmas_sugeridas=len(selecionadas),
        horas_formacao_total=sum(c.calendario.carga_horaria_total for c in selecionadas),
        objetivo_valor=resultado_solver.objetivo_valor,
        status_solver=resultado_solver.status,
        tempo_execucao_seg=resultado_solver.tempo_execucao_seg,
    )

    return ResultadoMetricas(
        pct_ociosidade=pct_ociosidade,
        utilizacao_por_instrutor=tuple(utilizacoes),
        indice_balanceamento_carga=indice_balanceamento_carga,
        distribuicao_por_tipologia=distribuicao_tipologia,
        indice_balanceamento_tipologias=indice_balanceamento_tipologias,
        primeira_data_livre=primeira_data_livre,
        oportunidades=oportunidades,
        horas_reposicao_sexta=horas_reposicao,
        metadados=metadados,
    )


def _calcular_utilizacao_por_instrutor(
    instrutores: list[InstrutorDados],
    selecionadas: tuple[Candidata, ...],
    ocupacao: Ocupacao,
    periodo_de: date,
    periodo_ate: date,
) -> list[UtilizacaoInstrutor]:
    horas_por_instrutor: dict[int, float] = {}
    for c in selecionadas:
        horas_por_instrutor[c.instrutor_id] = (
            horas_por_instrutor.get(c.instrutor_id, 0.0) + c.calendario.carga_horaria_total
        )

    resultado = []
    for instrutor in instrutores:
        dias = dias_uteis_no_periodo(instrutor.dias_semana, periodo_de, periodo_ate)
        disponivel = sum(capacidade * dias for capacidade in instrutor.turnos.values())

        ocupado_bruto = ocupado_fixo_total(ocupacao, instrutor.id)
        ocupado = disponivel if ocupado_bruto == float("inf") else min(ocupado_bruto, disponivel)

        alocado = ocupado + horas_por_instrutor.get(instrutor.id, 0.0)
        resultado.append(
            UtilizacaoInstrutor(
                instrutor_id=instrutor.id,
                horas_alocadas=min(alocado, disponivel),
                horas_disponiveis=disponivel,
            )
        )
    return resultado


def _distribuicao_por_tipologia(
    selecionadas: tuple[Candidata, ...], universo: set[int]
) -> dict[int, int]:
    """Conta turmas selecionadas por tipologia, com 0 para as sem nenhuma seleção."""
    distribuicao: dict[int, int] = dict.fromkeys(universo, 0)
    for c in selecionadas:
        distribuicao[c.tipologia_id] = distribuicao.get(c.tipologia_id, 0) + 1
    return distribuicao


def _primeira_data_livre_por_instrutor(
    instrutores: list[InstrutorDados],
    turmas_andamento: list[TurmaAndamentoDados],
    periodo_de: date,
) -> dict[int, date]:
    """Primeira data em que o instrutor fica livre em todos os turnos.

    Baseada na data de término **oficial** (`data_fim_prevista`) das turmas em
    andamento — não no último encontro efetivo do padrão de dias. É assim que
    a equipe de mobilização acompanha o compromisso ("a turma termina em
    30/08" → instrutor livre a partir de 31/08), independentemente de o
    padrão de dias fazer o último encontro efetivo cair um ou dois dias antes.

    Instrutor sem nenhuma turma em andamento tem como primeira data livre o
    início do próprio período.
    """
    ultimo_fim_por_turno: dict[tuple[int, Turno], date] = {}
    for turma in turmas_andamento:
        chave = (turma.instrutor_id, turma.turno)
        atual = ultimo_fim_por_turno.get(chave)
        if atual is None or turma.data_fim_prevista > atual:
            ultimo_fim_por_turno[chave] = turma.data_fim_prevista

    resultado: dict[int, date] = {}
    for instrutor in instrutores:
        livre_por_turno = [
            periodo_de
            if (fim := ultimo_fim_por_turno.get((instrutor.id, turno))) is None
            else max(fim + timedelta(days=1), periodo_de)
            for turno in instrutor.turnos
        ]
        resultado[instrutor.id] = max(livre_por_turno) if livre_por_turno else periodo_de

    return resultado


def _leque_de_oportunidades(
    candidatas: list[Candidata],
) -> tuple[OportunidadeTipologia, ...]:
    """Agrupa as candidatas geradas por (tipologia, data de início).

    Representa o leque completo de possibilidades — não apenas o que o
    solver escolheu — para responder "o que poderia ser aberto e quando".
    """
    grupos: dict[tuple[int, date], list[int]] = {}
    for c in candidatas:
        chave = (c.tipologia_id, c.calendario.data_inicio)
        grupos.setdefault(chave, []).append(c.instrutor_id)

    oportunidades = [
        OportunidadeTipologia(
            tipologia_id=tipologia_id,
            data_inicio=data_inicio,
            instrutor_ids=tuple(sorted(set(instrutor_ids))),
            total_turmas=len(instrutor_ids),
        )
        for (tipologia_id, data_inicio), instrutor_ids in grupos.items()
    ]
    return tuple(sorted(oportunidades, key=lambda o: (o.data_inicio, o.tipologia_id)))


def _horas_reposicao_sexta(
    instrutores: list[InstrutorDados], periodo_de: date, periodo_ate: date
) -> float:
    """Capacidade de reposição disponível às sextas-feiras.

    Derivada dos instrutores que declararam disponibilidade no dia 6 — nunca
    aloca turma regular, apenas informa a capacidade de contingência.
    """
    sextas_no_periodo = 0
    data_atual = periodo_de
    while data_atual <= periodo_ate:
        if data_atual.isoweekday() == 5:  # sexta-feira em ISO
            sextas_no_periodo += 1
        data_atual += timedelta(days=1)

    total = 0.0
    for instrutor in instrutores:
        if DIA_REPOSICAO not in instrutor.dias_semana:
            continue
        total += sum(instrutor.turnos.values()) * sextas_no_periodo

    return total

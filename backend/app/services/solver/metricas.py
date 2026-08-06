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
    slots_disponiveis_periodo,
    slots_ocupados_total,
)


@dataclass(frozen=True)
class UtilizacaoInstrutor:
    instrutor_id: int
    slots_alocados: int
    slots_disponiveis: int

    @property
    def utilizacao_percentual(self) -> float:
        if self.slots_disponiveis <= 0:
            return 0.0
        return min(self.slots_alocados / self.slots_disponiveis, 1.0) * 100


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
    primeira_data_livre_por_slot: dict[int, dict[Turno, date]]
    oportunidades: tuple[OportunidadeTipologia, ...]
    slots_reposicao_sexta: int
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
    ocupacao = calcular_ocupacao(turmas_andamento)

    utilizacoes = _calcular_utilizacao_por_instrutor(
        instrutores, selecionadas, ocupacao, periodo_de, periodo_ate
    )

    slots_alocados_total = sum(u.slots_alocados for u in utilizacoes)
    slots_disponiveis_total = sum(u.slots_disponiveis for u in utilizacoes)
    pct_ociosidade = (
        (1 - slots_alocados_total / slots_disponiveis_total) * 100
        if slots_disponiveis_total > 0
        else 0.0
    )

    utilizacoes_validas = [u.utilizacao_percentual for u in utilizacoes if u.slots_disponiveis > 0]
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

    primeira_data_livre_por_slot = _primeira_data_livre_por_slot(
        instrutores, turmas_andamento, periodo_de
    )
    primeira_data_livre = {
        instrutor_id: min(datas.values()) if datas else periodo_de
        for instrutor_id, datas in primeira_data_livre_por_slot.items()
    }

    oportunidades = _leque_de_oportunidades(candidatas_geradas)

    slots_reposicao = _slots_reposicao_sexta(instrutores, periodo_de, periodo_ate)

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
        primeira_data_livre_por_slot=primeira_data_livre_por_slot,
        oportunidades=oportunidades,
        slots_reposicao_sexta=slots_reposicao,
        metadados=metadados,
    )


def _calcular_utilizacao_por_instrutor(
    instrutores: list[InstrutorDados],
    selecionadas: tuple[Candidata, ...],
    ocupacao: Ocupacao,
    periodo_de: date,
    periodo_ate: date,
) -> list[UtilizacaoInstrutor]:
    slots_por_instrutor: dict[int, int] = {}
    for c in selecionadas:
        slots_por_instrutor[c.instrutor_id] = (
            slots_por_instrutor.get(c.instrutor_id, 0) + len(c.calendario.encontros)
        )

    resultado = []
    for instrutor in instrutores:
        disponivel = slots_disponiveis_periodo(instrutor, periodo_de, periodo_ate)
        ocupado_fixo = slots_ocupados_total(ocupacao, instrutor.id, periodo_de, periodo_ate)

        alocado = ocupado_fixo + slots_por_instrutor.get(instrutor.id, 0)
        resultado.append(
            UtilizacaoInstrutor(
                instrutor_id=instrutor.id,
                slots_alocados=min(alocado, disponivel),
                slots_disponiveis=disponivel,
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


def _primeira_data_livre_por_slot(
    instrutores: list[InstrutorDados],
    turmas_andamento: list[TurmaAndamentoDados],
    periodo_de: date,
) -> dict[int, dict[Turno, date]]:
    """Primeira data em que cada slot do instrutor fica livre.

    Cada slot libera de forma independente — quem consome o agregado (ver
    `primeira_data_livre` em `calcular_metricas`) usa o mínimo entre eles, não
    o máximo: um instrutor com um slot livre amanhã e outro ocupado por meses
    já tem oportunidade de curto prazo, e reportar o máximo esconderia isso.

    Baseada na data de término **oficial** (`data_fim_prevista`) das turmas em
    andamento — não no último encontro efetivo do padrão de dias. É assim que
    a equipe de mobilização acompanha o compromisso ("a turma termina em
    30/08" → instrutor livre a partir de 31/08), independentemente de o
    padrão de dias fazer o último encontro efetivo cair um ou dois dias antes.

    Instrutor sem nenhuma turma em andamento tem como primeira data livre o
    início do próprio período, em todos os seus slots.
    """
    ultimo_fim_por_slot: dict[tuple[int, Turno], date] = {}
    for turma in turmas_andamento:
        chave = (turma.instrutor_id, turma.turno)
        atual = ultimo_fim_por_slot.get(chave)
        if atual is None or turma.data_fim_prevista > atual:
            ultimo_fim_por_slot[chave] = turma.data_fim_prevista

    resultado: dict[int, dict[Turno, date]] = {}
    for instrutor in instrutores:
        resultado[instrutor.id] = {
            turno: (
                periodo_de
                if (fim := ultimo_fim_por_slot.get((instrutor.id, turno))) is None
                else max(fim + timedelta(days=1), periodo_de)
            )
            for turno in instrutor.turnos
        }

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


def _slots_reposicao_sexta(
    instrutores: list[InstrutorDados], periodo_de: date, periodo_ate: date
) -> int:
    """Quantidade de slots de reposição disponíveis às sextas-feiras.

    Derivada dos instrutores que declararam disponibilidade no dia 6 — nunca
    aloca turma regular, apenas informa a capacidade de contingência.
    """
    sextas_no_periodo = 0
    data_atual = periodo_de
    while data_atual <= periodo_ate:
        if data_atual.isoweekday() == 5:  # sexta-feira em ISO
            sextas_no_periodo += 1
        data_atual += timedelta(days=1)

    total = 0
    for instrutor in instrutores:
        if DIA_REPOSICAO not in instrutor.dias_semana:
            continue
        total += len(instrutor.turnos) * sextas_no_periodo

    return total

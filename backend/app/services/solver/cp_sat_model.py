"""Modelo CP-SAT: restrições rígidas e objetivo composto.

Cada candidata (ver `gerador_candidatas`) vira uma variável booleana `z[c]`.
Não há variável de "gap": uma candidata não escolhida simplesmente não entra
na solução, e o modelo é sempre viável — a solução vazia ("não abrir nada") é
uma resposta válida, nunca `INFEASIBLE`.

Encadeamento: a restrição de capacidade é por (instrutor, data, turno), não um
flag global de "instrutor ocupado". Como todas as candidatas de todas as
semanas do período coexistem no modelo, o solver escolhe a sequência inteira
de aberturas de uma vez — é isso que produz o pipeline, não uma lógica
turma-a-turma.
"""

from dataclasses import dataclass
from datetime import date

from ortools.sat.python import cp_model

from app.services.solver.dados import InstrutorDados, TipologiaDados, TurmaAndamentoDados
from app.services.solver.gerador_candidatas import Candidata
from app.services.solver.ocupacao import (
    Ocupacao,
    calcular_ocupacao,
    horas_disponiveis_periodo,
    ocupado_fixo_total,
)

MAX_TURMAS_POR_DIA = 4

# Horas podem ser fracionárias (ex.: 3.5h); o CP-SAT exige coeficientes
# inteiros em suas restrições e objetivo, então toda grandeza em horas é
# escalada antes de entrar no modelo. Fator 2 cobre valores em meias-horas.
ESCALA_HORAS = 2

# Escala da utilização percentual usada no termo de equilíbrio de carga.
ESCALA_UTILIZACAO = 1000

# Granularidade para converter pesos/normalizadores (fracionários) em
# coeficientes inteiros da função objetivo, sem perder precisão relevante.
GRANULARIDADE_OBJETIVO = 1_000_000


def _escalar_horas(valor: float) -> int:
    return round(valor * ESCALA_HORAS)


@dataclass(frozen=True)
class PesosObjetivo:
    """Pesos dos quatro critérios do objetivo composto — todos não negativos."""

    maximizar_aproveitamento: float
    antecipar_inicio: float
    balancear_carga_instrutores: float
    balancear_tipologias: float


@dataclass(frozen=True)
class Normalizadores:
    """Fatores de normalização de cada termo do objetivo.

    Referências de magnitude máxima plausível — evitam que um termo domine os
    demais só por diferença de escala. Persistidos junto ao cenário para que
    comparações entre simulações permaneçam válidas.
    """

    aproveitamento: float
    antecipacao: float
    equilibrio_carga: float
    equilibrio_tipologias: float


@dataclass(frozen=True)
class ConfiguracaoSolver:
    """Parâmetros de execução do solver.

    `gap_relativo` permite ao CP-SAT reportar OTIMO para qualquer solução
    dentro dessa distância do melhor limite provado — sem exigir a prova
    exata. Isso tem uma consequência importante: com `num_workers > 1`, QUAL
    solução dentro dessa margem é encontrada depende do timing das buscas
    paralelas, então duas execuções podem retornar seleções diferentes (ambas
    dentro da margem) mesmo com a mesma semente. Determinismo byte-a-byte só é
    garantido com `gap_relativo=0.0` (exigindo prova exata de otimalidade);
    valores maiores trocam essa garantia por velocidade.
    """

    time_limit_seg: float = 180
    num_workers: int = 8
    gap_relativo: float = 0.02
    seed: int = 42


@dataclass(frozen=True)
class ResultadoSolver:
    status: str  # OTIMO | FACTIVEL | INFACTIVEL | MODELO_INVALIDO | DESCONHECIDO
    objetivo_valor: float | None
    tempo_execucao_seg: float
    candidatas_selecionadas: tuple[Candidata, ...]


def normalizadores_padrao(
    candidatas: list[Candidata],
    instrutores: list[InstrutorDados],
    periodo_de: date,
    periodo_ate: date,
) -> Normalizadores:
    """Estima os fatores de normalização a partir da capacidade real do cenário.

    O aproveitamento é normalizado pela **capacidade total disponível** dos
    instrutores no período — nunca pela soma bruta de todas as candidatas.
    A maioria das candidatas compete pelo mesmo instrutor/turno/data e jamais
    poderia ser aberta simultaneamente, então usar essa soma como teto
    superestima muito o aproveitamento realisticamente alcançável. Isso
    inflaria artificialmente o normalizador (encolhendo o coeficiente de
    aproveitamento) e faria o termo de equilíbrio de carga — cujo teto fixo é
    apenas 1000 — dominar o objetivo por um fator de escala, não por peso real
    escolhido pelo usuário.
    """
    capacidade_total = sum(
        horas_disponiveis_periodo(i, periodo_de, periodo_ate) for i in instrutores
    )
    aproveitamento = capacidade_total or 1.0

    if not candidatas:
        return Normalizadores(
            aproveitamento=aproveitamento,
            antecipacao=1.0,
            equilibrio_carga=float(ESCALA_UTILIZACAO),
            equilibrio_tipologias=1.0,
        )

    semana_max = max(c.semana_inicio for c in candidatas)
    # Teto realista: no melhor caso, cada instrutor abre uma turma na semana 0.
    antecipacao = max(semana_max * max(len(instrutores), 1), 1)

    contagem_por_tipologia: dict[int, int] = {}
    for c in candidatas:
        contagem_por_tipologia[c.tipologia_id] = contagem_por_tipologia.get(c.tipologia_id, 0) + 1
    equilibrio_tipologias = max(contagem_por_tipologia.values()) if contagem_por_tipologia else 1

    return Normalizadores(
        aproveitamento=float(aproveitamento),
        antecipacao=float(antecipacao),
        equilibrio_carga=float(ESCALA_UTILIZACAO),
        equilibrio_tipologias=float(equilibrio_tipologias),
    )


def resolver(
    *,
    candidatas: list[Candidata],
    instrutores: list[InstrutorDados],
    tipologias: dict[int, TipologiaDados],
    turmas_andamento: list[TurmaAndamentoDados],
    periodo_de: date,
    periodo_ate: date,
    pesos: PesosObjetivo,
    normalizadores: Normalizadores | None = None,
    configuracao: ConfiguracaoSolver | None = None,
) -> ResultadoSolver:
    """Resolve o modelo e devolve as candidatas selecionadas.

    `instrutores` e `tipologias` devem ser os mesmos usados para gerar
    `candidatas` — precisam descrever exatamente o mesmo universo em jogo, já
    filtrado por escopo e compartilhamento.
    """
    configuracao = configuracao or ConfiguracaoSolver()
    normalizadores = normalizadores or normalizadores_padrao(
        candidatas, instrutores, periodo_de, periodo_ate
    )

    model = cp_model.CpModel()
    z = {c.id: model.NewBoolVar(f"z_{c.id}") for c in candidatas}

    # Recalcula a ocupação (barato) a partir dos mesmos dados usados na
    # geração das candidatas, para alimentar as restrições de capacidade e
    # teto diário.
    ocupacao = calcular_ocupacao(turmas_andamento, tipologias)

    _restringir_capacidade_horaria(model, z, candidatas, instrutores, ocupacao)
    _restringir_teto_diario(model, z, candidatas, ocupacao)

    semana_max = max((c.semana_inicio for c in candidatas), default=0)

    termo1 = _termo_aproveitamento(z, candidatas)
    termo2 = _termo_antecipacao(z, candidatas, semana_max)
    termo3 = _termo_equilibrio_carga(
        model, z, candidatas, instrutores, periodo_de, periodo_ate, ocupacao
    )
    termo4 = _termo_equilibrio_tipologias(model, z, candidatas)

    coef1 = _coeficiente(pesos.maximizar_aproveitamento, normalizadores.aproveitamento)
    coef2 = _coeficiente(pesos.antecipar_inicio, normalizadores.antecipacao)
    coef3 = _coeficiente(pesos.balancear_carga_instrutores, normalizadores.equilibrio_carga)
    coef4 = _coeficiente(pesos.balancear_tipologias, normalizadores.equilibrio_tipologias)

    objetivo_expr = coef1 * termo1 + coef2 * termo2 - coef3 * termo3 - coef4 * termo4
    model.Maximize(objetivo_expr)

    solver = cp_model.CpSolver()
    _configurar_parametros(solver, configuracao)
    status = solver.Solve(model)

    if status == cp_model.OPTIMAL:
        # Com múltiplos workers, buscas paralelas empatadas em soluções
        # igualmente ótimas podem convergir para candidatas diferentes a cada
        # execução — o valor do objetivo se repete, mas a seleção não. Uma
        # segunda passagem fixa o valor já provado e resolve de novo com um
        # critério de desempate canônico (soma dos IDs selecionados) em
        # thread única, eliminando essa variação.
        return _resolver_com_desempate(model, z, candidatas, objetivo_expr, solver, configuracao)

    resolvido = status == cp_model.FEASIBLE
    return ResultadoSolver(
        status=_status_texto(status),
        objetivo_valor=solver.ObjectiveValue() if resolvido else None,
        tempo_execucao_seg=solver.WallTime(),
        candidatas_selecionadas=(
            tuple(c for c in candidatas if solver.Value(z[c.id])) if resolvido else ()
        ),
    )


def _configurar_parametros(
    solver: cp_model.CpSolver, configuracao: ConfiguracaoSolver, num_workers: int | None = None
) -> None:
    solver.parameters.max_time_in_seconds = configuracao.time_limit_seg
    solver.parameters.num_workers = configuracao.num_workers if num_workers is None else num_workers
    solver.parameters.relative_gap_limit = configuracao.gap_relativo
    solver.parameters.random_seed = configuracao.seed


# Teto de tempo da passagem de desempate: ela parte de um ponto já viável
# (hint da 1ª fase), então não precisa do orçamento de tempo completo — um
# valor pequeno evita que uma busca-fantasma consuma minutos à toa em
# cenários grandes, como visto no benchmark (170k+ candidatas).
TEMPO_MAXIMO_DESEMPATE_SEG = 15.0


def _resolver_com_desempate(
    model: cp_model.CpModel,
    z: dict[int, cp_model.IntVar],
    candidatas: list[Candidata],
    objetivo_expr,
    solver_fase1: cp_model.CpSolver,
    configuracao: ConfiguracaoSolver,
) -> ResultadoSolver:
    valor_otimo = round(solver_fase1.ObjectiveValue())

    # Hint com a solução já encontrada: a passagem de desempate parte de um
    # ponto viável conhecido, em vez de buscar do zero — sem isso, fixar o
    # objetivo em uma igualdade exata pode levar tanto quanto (ou mais que) a
    # busca original, especialmente em problemas grandes e simétricos.
    for c in candidatas:
        model.AddHint(z[c.id], solver_fase1.Value(z[c.id]))

    model.Add(objetivo_expr == valor_otimo)
    model.Minimize(sum(c.id * z[c.id] for c in candidatas))

    solver_fase2 = cp_model.CpSolver()
    configuracao_fase2 = ConfiguracaoSolver(
        time_limit_seg=min(configuracao.time_limit_seg, TEMPO_MAXIMO_DESEMPATE_SEG),
        num_workers=1,  # thread única: é o que garante o desempate determinístico
        gap_relativo=configuracao.gap_relativo,
        seed=configuracao.seed,
    )
    _configurar_parametros(solver_fase2, configuracao_fase2)
    status2 = solver_fase2.Solve(model)

    tempo_total = solver_fase1.WallTime() + solver_fase2.WallTime()

    if status2 not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        # Não deveria ocorrer — o hint já é uma solução viável conhecida — mas
        # cai para o resultado da 1ª fase em vez de falhar.
        return ResultadoSolver(
            status="OTIMO",
            objetivo_valor=valor_otimo,
            tempo_execucao_seg=tempo_total,
            candidatas_selecionadas=tuple(c for c in candidatas if solver_fase1.Value(z[c.id])),
        )

    return ResultadoSolver(
        status="OTIMO",
        objetivo_valor=valor_otimo,
        tempo_execucao_seg=tempo_total,
        candidatas_selecionadas=tuple(c for c in candidatas if solver_fase2.Value(z[c.id])),
    )


def _coeficiente(peso: float, normalizador: float) -> int:
    normalizador = normalizador or 1.0
    return round(GRANULARIDADE_OBJETIVO * peso / normalizador)


def _status_texto(status: int) -> str:
    return {
        cp_model.OPTIMAL: "OTIMO",
        cp_model.FEASIBLE: "FACTIVEL",
        cp_model.INFEASIBLE: "INFACTIVEL",
        cp_model.MODEL_INVALID: "MODELO_INVALIDO",
    }.get(status, "DESCONHECIDO")


# --------------------------------------------------------------------------
# Restrições rígidas
# --------------------------------------------------------------------------


def _restringir_capacidade_horaria(
    model: cp_model.CpModel,
    z: dict[int, cp_model.IntVar],
    candidatas: list[Candidata],
    instrutores: list[InstrutorDados],
    ocupacao: Ocupacao,
) -> None:
    """Para cada (instrutor, turno, data) tocada por alguma candidata: horas
    escolhidas + ocupação de turmas em andamento não podem exceder a
    capacidade daquele turno."""
    capacidade_por_instrutor_turno = {
        (i.id, turno): cap for i in instrutores for turno, cap in i.turnos.items()
    }

    grupos: dict[tuple, list[tuple[int, float]]] = {}
    for c in candidatas:
        for encontro in c.calendario.encontros:
            chave = (c.instrutor_id, encontro.turno, encontro.data)
            grupos.setdefault(chave, []).append((c.id, encontro.horas))

    for (instrutor_id, turno, data), itens in grupos.items():
        capacidade = capacidade_por_instrutor_turno.get((instrutor_id, turno), 0.0)
        ocupado_fixo = ocupacao.horas_por_turno_data.get((instrutor_id, turno, data), 0.0)

        if ocupado_fixo == float("inf") or ocupado_fixo >= capacidade:
            # A ocupação fixa já esgota a capacidade: nenhuma candidata cabe
            # ali. Na prática o gerador de candidatas já poda esses casos;
            # esta restrição é uma defesa adicional.
            for candidato_id, _ in itens:
                model.Add(z[candidato_id] == 0)
            continue

        limite = _escalar_horas(capacidade - ocupado_fixo)
        model.Add(
            sum(_escalar_horas(horas) * z[candidato_id] for candidato_id, horas in itens)
            <= limite
        )


def _restringir_teto_diario(
    model: cp_model.CpModel,
    z: dict[int, cp_model.IntVar],
    candidatas: list[Candidata],
    ocupacao: Ocupacao,
) -> None:
    """Limita a 4 o total de turmas (sugeridas + em andamento) por instrutor e dia."""
    grupos: dict[tuple[int, date], list[int]] = {}
    for c in candidatas:
        for data in {e.data for e in c.calendario.encontros}:
            grupos.setdefault((c.instrutor_id, data), []).append(c.id)

    for (instrutor_id, data), candidatos_ids in grupos.items():
        ja_ocupadas = ocupacao.turmas_por_data.get((instrutor_id, data), 0)
        limite = MAX_TURMAS_POR_DIA - ja_ocupadas
        if limite < 0:
            for cid in candidatos_ids:
                model.Add(z[cid] == 0)
            continue
        model.Add(sum(z[cid] for cid in candidatos_ids) <= limite)


# --------------------------------------------------------------------------
# Termos do objetivo
# --------------------------------------------------------------------------


def _termo_aproveitamento(z: dict[int, cp_model.IntVar], candidatas: list[Candidata]):
    """T1 — soma das horas de formação das turmas abertas."""
    return sum(_escalar_horas(c.calendario.carga_horaria_total) * z[c.id] for c in candidatas)


def _termo_antecipacao(
    z: dict[int, cp_model.IntVar], candidatas: list[Candidata], semana_max: int
):
    """T2 — favorece semanas de início mais cedo (quanto menor, maior o termo)."""
    return sum((semana_max - c.semana_inicio) * z[c.id] for c in candidatas)


def _termo_equilibrio_carga(
    model: cp_model.CpModel,
    z: dict[int, cp_model.IntVar],
    candidatas: list[Candidata],
    instrutores: list[InstrutorDados],
    periodo_de: date,
    periodo_ate: date,
    ocupacao: Ocupacao,
) -> cp_model.IntVar:
    """T3 — range (máximo − mínimo) da utilização percentual entre instrutores.

    Utilização em escala 0–1000, não em horas brutas, para não penalizar
    injustamente quem tem menor capacidade declarada.
    """
    utilizacoes: list[cp_model.IntVar] = []

    for instrutor in instrutores:
        disponivel_scaled = round(
            horas_disponiveis_periodo(instrutor, periodo_de, periodo_ate) * ESCALA_HORAS
        )
        if disponivel_scaled <= 0:
            continue  # sem capacidade no período; não entra no balanceamento

        ocupado_bruto = ocupado_fixo_total(ocupacao, instrutor.id)
        ocupado_scaled = (
            disponivel_scaled
            if ocupado_bruto == float("inf")
            else min(round(ocupado_bruto * ESCALA_HORAS), disponivel_scaled)
        )

        candidatas_do_instrutor = [c for c in candidatas if c.instrutor_id == instrutor.id]
        alocado_expr = ocupado_scaled + sum(
            _escalar_horas(c.calendario.carga_horaria_total) * z[c.id]
            for c in candidatas_do_instrutor
        )

        util_var = model.NewIntVar(0, ESCALA_UTILIZACAO, f"util_{instrutor.id}")
        model.AddDivisionEquality(util_var, alocado_expr * ESCALA_UTILIZACAO, disponivel_scaled)
        utilizacoes.append(util_var)

    if not utilizacoes:
        return model.NewConstant(0)

    util_max = model.NewIntVar(0, ESCALA_UTILIZACAO, "util_max")
    util_min = model.NewIntVar(0, ESCALA_UTILIZACAO, "util_min")
    model.AddMaxEquality(util_max, utilizacoes)
    model.AddMinEquality(util_min, utilizacoes)

    termo = model.NewIntVar(0, ESCALA_UTILIZACAO, "equilibrio_carga")
    model.Add(termo == util_max - util_min)
    return termo


def _termo_equilibrio_tipologias(
    model: cp_model.CpModel, z: dict[int, cp_model.IntVar], candidatas: list[Candidata]
) -> cp_model.IntVar:
    """T4 — range da contagem de turmas abertas por tipologia.

    Calculado só sobre as tipologias efetivamente ofertáveis no cenário (as
    que têm ao menos uma candidata) — não há meta de demanda a perseguir.
    """
    candidatas_por_tipologia: dict[int, list[Candidata]] = {}
    for c in candidatas:
        candidatas_por_tipologia.setdefault(c.tipologia_id, []).append(c)

    if len(candidatas_por_tipologia) < 2:
        # Zero ou uma tipologia ofertável: não há o que equilibrar.
        return model.NewConstant(0)

    max_por_tipologia = max(len(cands) for cands in candidatas_por_tipologia.values())

    contagens = []
    for tipologia_id in sorted(candidatas_por_tipologia):
        cands = candidatas_por_tipologia[tipologia_id]
        contagem_var = model.NewIntVar(0, max_por_tipologia, f"contagem_tipologia_{tipologia_id}")
        model.Add(contagem_var == sum(z[c.id] for c in cands))
        contagens.append(contagem_var)

    cont_max = model.NewIntVar(0, max_por_tipologia, "contagem_max")
    cont_min = model.NewIntVar(0, max_por_tipologia, "contagem_min")
    model.AddMaxEquality(cont_max, contagens)
    model.AddMinEquality(cont_min, contagens)

    termo = model.NewIntVar(0, max_por_tipologia, "equilibrio_tipologias")
    model.Add(termo == cont_max - cont_min)
    return termo

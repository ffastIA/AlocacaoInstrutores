"""Benchmark do motor de simulação no teto de escala esperado.

Gera dados sintéticos de ~60 instrutores e um horizonte de ~35 semanas,
medindo o número de candidatas geradas e o tempo de resolução — os dois
números que decidem se alguma estratégia de poda adicional é necessária
(ver "Pontos em aberto" no design da change `add-class-opening-simulator`).

Uso:
    python scripts/benchmark_solver.py

Resultado observado (semente=42, disponibilidade sintética realista — não o
pior caso "todos aptos a tudo"):

    6.318 candidatas geradas em ~0.3s
    Resolução (gap_relativo=0.02, 8 workers + desempate em 1 thread): ~20-22s
    685 turmas sugeridas, ~83% de aproveitamento (~17% de ociosidade)

Bem abaixo do teto pessimista de ~170 mil candidatas estimado no design —
nenhuma estratégia de poda adicional (grid quinzenal/mensal, janelas
deslizantes) se mostrou necessária nesta escala. Duas correções relevantes
nasceram deste benchmark, ambas já aplicadas em `cp_sat_model.py`:

1. Os normalizadores padrão inicialmente usavam a soma bruta de TODAS as
   candidatas como teto de aproveitamento — um teto irreal, já que a maioria
   compete pelo mesmo instrutor/turno/data. Isso fazia o termo de equilíbrio
   de carga pesar ~100x mais por unidade que o de aproveitamento mesmo com
   pesos de usuário parecidos (0.4 vs 0.2), levando o solver a considerar
   "não abrir nada" como ótimo. Corrigido usando a capacidade real disponível
   dos instrutores como teto.
2. A segunda passagem de desempate determinístico (que fixa o valor ótimo e
   busca a seleção canônica) buscava do zero, levando até o limite de tempo
   inteiro sem sucesso em cenários grandes (129s de parede vs. 7.6s
   reportados). Corrigido com `AddHint` — a segunda busca agora parte da
   solução já encontrada na 1ª fase, caindo para ~20-22s totais.
"""

import random
import sys
import time
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.models.enums import Turno  # noqa: E402
from app.services.solver.cp_sat_model import (  # noqa: E402
    ConfiguracaoSolver,
    PesosObjetivo,
    resolver,
)
from app.services.solver.dados import InstrutorDados, TipologiaDados  # noqa: E402
from app.services.solver.gerador_candidatas import gerar_candidatas  # noqa: E402
from app.services.solver.metricas import calcular_metricas  # noqa: E402

SEMENTE = 42
NUM_INSTRUTORES = 60
NUM_SEMANAS = 35
PERIODO_DE = date(2026, 8, 31)  # segunda-feira

TIPOLOGIAS_BASE = [
    # (nome, carga_horaria_total, horas_por_encontro)
    ("Programação", 60, 3),
    ("Pixel Art", 24, 2),
    ("Robótica", 40, 4),
    ("Google Workspace", 30, 3),
    ("Design Gráfico", 36, 3),
    ("Edição de Vídeo", 48, 4),
]


def gerar_dados_sinteticos() -> tuple[list[InstrutorDados], dict[int, TipologiaDados]]:
    aleatorio = random.Random(SEMENTE)

    tipologias = {
        i: TipologiaDados(id=i, carga_horaria_total_horas=carga, horas_por_encontro=horas)
        for i, (_nome, carga, horas) in enumerate(TIPOLOGIAS_BASE, start=1)
    }

    instrutores = []
    for i in range(1, NUM_INSTRUTORES + 1):
        projeto_id = aleatorio.randint(1, 4)

        turnos_possiveis = list(Turno)
        n_turnos = aleatorio.choice([1, 1, 2])  # maioria com 1 turno, alguns com 2
        turnos_escolhidos = aleatorio.sample(turnos_possiveis, n_turnos)
        turnos = {
            t: aleatorio.choice([3.0, 4.0]) if t == Turno.NOITE else 4.0 for t in turnos_escolhidos
        }
        # Turno noturno nunca passa de 3h de capacidade.
        if Turno.NOITE in turnos:
            turnos[Turno.NOITE] = 3.0

        n_dias = aleatorio.choice([2, 2, 4])  # a maioria intercalada, alguns full
        dias_semana = (
            frozenset({2, 4}) if n_dias == 2 and aleatorio.random() < 0.5
            else frozenset({3, 5}) if n_dias == 2
            else frozenset({2, 3, 4, 5})
        )
        if aleatorio.random() < 0.2:
            dias_semana = dias_semana | {6}  # disponibilidade de reposição às sextas

        n_tipologias = aleatorio.choice([1, 1, 2, 2, 3])
        tipologia_ids = frozenset(
            aleatorio.sample(list(tipologias), min(n_tipologias, len(tipologias)))
        )

        instrutores.append(
            InstrutorDados(
                id=i,
                projeto_id=projeto_id,
                turnos=turnos,
                dias_semana=dias_semana,
                tipologia_ids=tipologia_ids,
            )
        )

    return instrutores, tipologias


def main() -> None:
    periodo_ate = PERIODO_DE + timedelta(weeks=NUM_SEMANAS)

    instrutores, tipologias = gerar_dados_sinteticos()

    print(f"=== Benchmark do motor de simulação (semente={SEMENTE}) ===")
    print(f"Instrutores: {len(instrutores)}")
    print(f"Tipologias: {len(tipologias)}")
    print(f"Período: {PERIODO_DE} a {periodo_ate} (~{NUM_SEMANAS} semanas)")
    print()

    t0 = time.perf_counter()
    candidatas = gerar_candidatas(
        instrutores=instrutores,
        tipologias=tipologias,
        turmas_andamento=[],
        periodo_de=PERIODO_DE,
        periodo_ate=periodo_ate,
        projetos_escopo=frozenset(),
        permitir_compartilhamento=False,
    )
    tempo_geracao = time.perf_counter() - t0

    print(f"Candidatas geradas: {len(candidatas)}")
    print(f"Tempo de geração/poda: {tempo_geracao:.3f}s")
    print()

    pesos = PesosObjetivo(
        maximizar_aproveitamento=0.4,
        antecipar_inicio=0.2,
        balancear_carga_instrutores=0.2,
        balancear_tipologias=0.2,
    )
    configuracao = ConfiguracaoSolver(time_limit_seg=120, num_workers=8, seed=SEMENTE)

    print("Resolvendo...")
    t0 = time.perf_counter()
    resultado = resolver(
        candidatas=candidatas,
        instrutores=instrutores,
        tipologias=tipologias,
        turmas_andamento=[],
        periodo_de=PERIODO_DE,
        periodo_ate=periodo_ate,
        pesos=pesos,
        configuracao=configuracao,
    )
    tempo_total = time.perf_counter() - t0

    print(f"Status do solver: {resultado.status}")
    print(f"Valor do objetivo: {resultado.objetivo_valor}")
    print(f"Tempo relatado pelo solver: {resultado.tempo_execucao_seg:.3f}s")
    print(f"Tempo total (parede): {tempo_total:.3f}s")
    print(f"Turmas sugeridas: {len(resultado.candidatas_selecionadas)}")
    print()

    metricas = calcular_metricas(
        resultado_solver=resultado,
        candidatas_geradas=candidatas,
        instrutores=instrutores,
        turmas_andamento=[],
        periodo_de=PERIODO_DE,
        periodo_ate=periodo_ate,
    )

    print("=== KPIs ===")
    print(f"Ociosidade: {metricas.pct_ociosidade:.1f}%")
    print(f"Horas de formação entregues: {metricas.metadados.horas_formacao_total:.0f}h")
    print(f"Índice de balanceamento de carga: {metricas.indice_balanceamento_carga:.1f}")
    print(f"Índice de balanceamento de tipologias: {metricas.indice_balanceamento_tipologias}")
    print(f"Distribuição por tipologia: {metricas.distribuicao_por_tipologia}")
    print(f"Horas de reposição (sextas): {metricas.horas_reposicao_sexta:.0f}h")
    print()

    print("=== Diagnóstico de escala ===")
    print(
        f"{len(candidatas)} candidatas para {len(instrutores)} instrutores "
        f"x {NUM_SEMANAS} semanas"
    )
    print(f"Tempo de geração: {tempo_geracao:.3f}s | Tempo de resolução: {tempo_total:.3f}s")


if __name__ == "__main__":
    main()

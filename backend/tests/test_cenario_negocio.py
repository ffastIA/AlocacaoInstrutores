"""Cenário de referência do negócio.

Este é o caso concreto que motivou o projeto inteiro: um instrutor que libera
capacidade numa data conhecida e domina duas tipologias deve gerar
oportunidades para as duas a partir daquela data — nunca para uma terceira
tipologia que ele não domina.
"""

from datetime import date

from app.models.enums import Modalidade, Turno
from app.services.solver.cp_sat_model import ConfiguracaoSolver, PesosObjetivo, resolver
from app.services.solver.dados import InstrutorDados, TipologiaDados, TurmaAndamentoDados
from app.services.solver.gerador_candidatas import gerar_candidatas
from app.services.solver.metricas import calcular_metricas

# "Instrutor que encerra turma em 30/08 dominando Pixel Art e Programação gera
# oportunidades dessas duas tipologias a partir de 31/08, e nenhuma de
# Robótica" — o exemplo textual usado para explicar o problema.
DATA_TERMINO_TURMA_ATUAL = date(2026, 8, 30)
PRIMEIRA_DATA_LIVRE = date(2026, 8, 31)

PERIODO_DE = date(2026, 8, 3)  # início do horizonte de simulação (bem antes do término)
PERIODO_ATE = date(2027, 4, 30)

PROGRAMACAO, PIXEL_ART, ROBOTICA = 1, 2, 3


def test_instrutor_libera_duas_tipologias_e_nenhuma_terceira() -> None:
    instrutor_multi = InstrutorDados(
        id=1,
        projeto_id=1,
        turnos={Turno.MANHA_1: 4.0},
        dias_semana=frozenset({2, 3, 4, 5}),
        tipologia_ids=frozenset({PROGRAMACAO, PIXEL_ART}),
    )
    # Segundo instrutor, apto só em Robótica — garante que a tipologia existe
    # no catálogo, mas que ninguém no cenário está livre para ministrá-la
    # nessa janela (ele está ocupado o período inteiro).
    instrutor_robotica = InstrutorDados(
        id=2,
        projeto_id=1,
        turnos={Turno.TARDE_1: 4.0},
        dias_semana=frozenset({2, 3, 4, 5}),
        tipologia_ids=frozenset({ROBOTICA}),
    )

    tipologias = {
        # Programação com 4h/encontro casa exatamente com a capacidade do
        # turno (4h) — garante que a turma em andamento ocupa o turno por
        # inteiro, sem sobra residual, nos dias em que ela ocorre.
        PROGRAMACAO: TipologiaDados(
            PROGRAMACAO, carga_horaria_total_horas=60, horas_por_encontro=4
        ),
        PIXEL_ART: TipologiaDados(PIXEL_ART, carga_horaria_total_horas=24, horas_por_encontro=2),
        ROBOTICA: TipologiaDados(ROBOTICA, carga_horaria_total_horas=40, horas_por_encontro=4),
    }

    turmas_andamento = [
        TurmaAndamentoDados(
            instrutor_id=1,
            tipologia_id=PROGRAMACAO,
            # Intensiva (seg-qui) cobre todos os dias disponíveis do
            # instrutor, então não sobra nenhum dia livre nesse turno até o
            # término — só a partir de 31/08 ele fica de fato disponível.
            modalidade=Modalidade.INTENSIVA_SEG_QUI,
            turno=Turno.MANHA_1,
            data_inicio=date(2026, 6, 1),
            data_fim_prevista=DATA_TERMINO_TURMA_ATUAL,
        ),
        TurmaAndamentoDados(
            instrutor_id=2,
            tipologia_id=ROBOTICA,
            modalidade=Modalidade.INTENSIVA_SEG_QUI,
            turno=Turno.TARDE_1,
            data_inicio=PERIODO_DE,
            data_fim_prevista=PERIODO_ATE,  # ocupado o período inteiro
        ),
    ]

    candidatas = gerar_candidatas(
        instrutores=[instrutor_multi, instrutor_robotica],
        tipologias=tipologias,
        turmas_andamento=turmas_andamento,
        periodo_de=PERIODO_DE,
        periodo_ate=PERIODO_ATE,
        projetos_escopo=frozenset(),
        permitir_compartilhamento=False,
    )

    # --- A pergunta central: quais tipologias podem abrir, e a partir de quando? ---
    tipologias_do_instrutor_multi = {
        c.tipologia_id for c in candidatas if c.instrutor_id == 1
    }
    assert tipologias_do_instrutor_multi == {PROGRAMACAO, PIXEL_ART}, (
        "o instrutor multi-tipologia deveria gerar oportunidades de Programação e "
        "Pixel Art, e nenhuma de Robótica (que ele não domina)"
    )

    datas_inicio_instrutor_multi = {
        c.calendario.data_inicio for c in candidatas if c.instrutor_id == 1
    }
    assert min(datas_inicio_instrutor_multi) >= PRIMEIRA_DATA_LIVRE, (
        "nenhuma oportunidade do instrutor deveria iniciar antes do término da turma atual"
    )

    # Robótica não deveria ter NENHUMA candidata no cenário: o único instrutor
    # apto está ocupado o período inteiro.
    assert not any(c.tipologia_id == ROBOTICA for c in candidatas), (
        "Robótica não deveria gerar oportunidade — o único instrutor apto está "
        "ocupado durante todo o período simulado"
    )

    # --- Resolver e conferir que o resultado reflete o leque de oportunidades ---
    resultado = resolver(
        candidatas=candidatas,
        instrutores=[instrutor_multi, instrutor_robotica],
        tipologias=tipologias,
        turmas_andamento=turmas_andamento,
        periodo_de=PERIODO_DE,
        periodo_ate=PERIODO_ATE,
        pesos=PesosObjetivo(
            maximizar_aproveitamento=0.4,
            antecipar_inicio=0.2,
            balancear_carga_instrutores=0.2,
            balancear_tipologias=0.2,
        ),
        configuracao=ConfiguracaoSolver(time_limit_seg=15, num_workers=4, seed=42),
    )

    assert resultado.status in ("OTIMO", "FACTIVEL")
    tipologias_selecionadas = {c.tipologia_id for c in resultado.candidatas_selecionadas}
    assert ROBOTICA not in tipologias_selecionadas

    # --- Métricas: o leque de oportunidades deve responder a pergunta de negócio ---
    metricas = calcular_metricas(
        resultado_solver=resultado,
        candidatas_geradas=candidatas,
        instrutores=[instrutor_multi, instrutor_robotica],
        turmas_andamento=turmas_andamento,
        periodo_de=PERIODO_DE,
        periodo_ate=PERIODO_ATE,
    )

    oportunidades_na_primeira_data = [
        o for o in metricas.oportunidades if o.data_inicio == PRIMEIRA_DATA_LIVRE
    ]
    tipologias_na_primeira_data = {o.tipologia_id for o in oportunidades_na_primeira_data}
    assert tipologias_na_primeira_data == {PROGRAMACAO, PIXEL_ART}, (
        "a partir de 31/08 deveriam aparecer exatamente duas oportunidades: "
        "Programação e Pixel Art"
    )

    assert metricas.primeira_data_livre[1] == PRIMEIRA_DATA_LIVRE

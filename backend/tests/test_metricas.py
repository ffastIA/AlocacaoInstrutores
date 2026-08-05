"""Testes do cálculo de métricas de uma simulação."""

from datetime import date, timedelta

from app.models.enums import Modalidade, Turno
from app.services.solver.cp_sat_model import (
    ConfiguracaoSolver,
    PesosObjetivo,
    resolver,
)
from app.services.solver.dados import InstrutorDados, TipologiaDados, TurmaAndamentoDados
from app.services.solver.gerador_candidatas import gerar_candidatas
from app.services.solver.metricas import calcular_metricas

PERIODO_DE = date(2026, 8, 31)  # segunda-feira
PERIODO_ATE = date(2027, 4, 30)

PESOS_APROVEITAMENTO = PesosObjetivo(1.0, 0.0, 0.0, 0.0)
CONFIG_RAPIDA = ConfiguracaoSolver(time_limit_seg=10, num_workers=4, seed=42)


def _instrutor(
    id: int,
    projeto_id: int = 1,
    turnos: dict[Turno, float] | None = None,
    dias_semana: frozenset[int] = frozenset({2, 3, 4, 5}),
    tipologia_ids: frozenset[int] = frozenset({1}),
) -> InstrutorDados:
    return InstrutorDados(
        id=id,
        projeto_id=projeto_id,
        turnos=turnos or {Turno.MANHA: 4.0},
        dias_semana=dias_semana,
        tipologia_ids=tipologia_ids,
    )


def _tipologia(id: int, carga_total: float = 40, horas_encontro: float = 4) -> TipologiaDados:
    return TipologiaDados(
        id=id, carga_horaria_total_horas=carga_total, horas_por_encontro=horas_encontro
    )


def _executar(
    instrutores,
    tipologias,
    turmas_andamento=None,
    pesos=PESOS_APROVEITAMENTO,
    periodo_ate=PERIODO_ATE,
):
    tipologias_dict = {t.id: t for t in tipologias}
    turmas_andamento = turmas_andamento or []
    candidatas = gerar_candidatas(
        instrutores=instrutores,
        tipologias=tipologias_dict,
        turmas_andamento=turmas_andamento,
        periodo_de=PERIODO_DE,
        periodo_ate=periodo_ate,
        projetos_escopo=frozenset(),
        permitir_compartilhamento=False,
    )
    resultado = resolver(
        candidatas=candidatas,
        instrutores=instrutores,
        tipologias=tipologias_dict,
        turmas_andamento=turmas_andamento,
        periodo_de=PERIODO_DE,
        periodo_ate=periodo_ate,
        pesos=pesos,
        configuracao=CONFIG_RAPIDA,
    )
    metricas = calcular_metricas(
        resultado_solver=resultado,
        candidatas_geradas=candidatas,
        instrutores=instrutores,
        turmas_andamento=turmas_andamento,
        periodo_de=PERIODO_DE,
        periodo_ate=periodo_ate,
    )
    return metricas, resultado, candidatas


class TestOciosidade:
    def test_capacidade_totalmente_ocupada_tem_ociosidade_zero(self) -> None:
        """Instrutor com turma em andamento cobrindo o período inteiro."""
        instrutor = _instrutor(1, turnos={Turno.MANHA: 4.0})
        turma_andamento = TurmaAndamentoDados(
            instrutor_id=1,
            tipologia_id=1,
            modalidade=Modalidade.INTENSIVA_SEG_QUI,
            turno=Turno.MANHA,
            data_inicio=PERIODO_DE,
            data_fim_prevista=PERIODO_ATE,
        )
        metricas, _, _ = _executar(
            [instrutor], [_tipologia(1)], turmas_andamento=[turma_andamento]
        )

        assert metricas.pct_ociosidade == 0.0

    def test_capacidade_parcialmente_ocupada(self) -> None:
        instrutor = _instrutor(1, turnos={Turno.MANHA: 4.0})
        metricas, resultado, _ = _executar(
            [instrutor], [_tipologia(1, carga_total=8, horas_encontro=4)]
        )

        assert 0.0 <= metricas.pct_ociosidade <= 100.0
        assert metricas.pct_ociosidade < 100.0  # ao menos uma turma foi aberta


class TestPrimeiraDataLivre:
    def test_instrutor_sem_alocacao_livre_desde_o_inicio(self) -> None:
        instrutor = _instrutor(1)
        metricas, _, _ = _executar([instrutor], [_tipologia(1)])

        assert metricas.primeira_data_livre[1] == PERIODO_DE

    def test_instrutor_com_turma_em_andamento_libera_apos_o_termino(self) -> None:
        fim_turma = date(2026, 10, 15)
        instrutor = _instrutor(1, turnos={Turno.MANHA: 4.0})
        turma_andamento = TurmaAndamentoDados(
            instrutor_id=1,
            tipologia_id=1,
            modalidade=Modalidade.INTENSIVA_SEG_QUI,
            turno=Turno.MANHA,
            data_inicio=PERIODO_DE,
            data_fim_prevista=fim_turma,
        )
        metricas, _, _ = _executar(
            [instrutor], [_tipologia(1)], turmas_andamento=[turma_andamento]
        )

        assert metricas.primeira_data_livre[1] == fim_turma + timedelta(days=1)


class TestDistribuicaoPorTipologia:
    def test_conta_turmas_por_tipologia(self) -> None:
        instrutor = _instrutor(1, turnos={Turno.MANHA: 4.0}, tipologia_ids=frozenset({1, 2}))
        metricas, resultado, _ = _executar(
            [instrutor],
            [
                _tipologia(1, carga_total=8, horas_encontro=4),
                _tipologia(2, carga_total=8, horas_encontro=4),
            ],
        )

        total_no_resultado = len(resultado.candidatas_selecionadas)
        assert sum(metricas.distribuicao_por_tipologia.values()) == total_no_resultado

    def test_tipologia_totalmente_excluida_conta_como_zero_no_indice(self) -> None:
        """Regressão: tipologia com zero turmas selecionadas não pode sumir do
        cálculo — senão o índice de desequilíbrio reportaria "equilíbrio
        perfeito" quando na verdade uma tipologia inteira ficou de fora."""
        instrutor = _instrutor(1, turnos={Turno.MANHA: 4.0}, tipologia_ids=frozenset({1, 2}))
        pesos_so_aproveitamento = PesosObjetivo(1.0, 0.0, 0.0, 0.0)
        metricas, resultado, candidatas = _executar(
            [instrutor],
            [
                _tipologia(1, carga_total=8, horas_encontro=4),
                _tipologia(2, carga_total=8, horas_encontro=4),
            ],
            pesos=pesos_so_aproveitamento,
            periodo_ate=date(2026, 11, 30),
        )

        tipologias_candidatas = {c.tipologia_id for c in candidatas}
        tipologias_selecionadas = {c.tipologia_id for c in resultado.candidatas_selecionadas}
        # Pré-condição do cenário: alguma tipologia candidata ficou de fora.
        assert tipologias_candidatas - tipologias_selecionadas

        assert set(metricas.distribuicao_por_tipologia) == tipologias_candidatas
        assert 0 in metricas.distribuicao_por_tipologia.values()
        assert metricas.indice_balanceamento_tipologias > 0


class TestLequeDeOportunidades:
    def test_instrutor_multi_tipologia_gera_oportunidades_das_duas(self) -> None:
        """Instrutor que domina Pixel Art e Programação: ambas aparecem no leque."""
        instrutor = _instrutor(1, tipologia_ids=frozenset({1, 2}))
        metricas, _, _ = _executar([instrutor], [_tipologia(1), _tipologia(2)])

        tipologias_no_leque = {o.tipologia_id for o in metricas.oportunidades}
        assert tipologias_no_leque == {1, 2}

    def test_tipologia_sem_instrutor_apto_nao_aparece(self) -> None:
        instrutor = _instrutor(1, tipologia_ids=frozenset({1}))
        metricas, _, _ = _executar([instrutor], [_tipologia(1)])

        assert all(o.tipologia_id == 1 for o in metricas.oportunidades)

    def test_ordenado_cronologicamente(self) -> None:
        instrutor = _instrutor(1, tipologia_ids=frozenset({1, 2}))
        metricas, _, _ = _executar([instrutor], [_tipologia(1), _tipologia(2)])

        datas = [o.data_inicio for o in metricas.oportunidades]
        assert datas == sorted(datas)

    def test_oportunidade_reflete_instrutor_que_a_sustenta(self) -> None:
        instrutor = _instrutor(1, tipologia_ids=frozenset({1}))
        metricas, _, _ = _executar([instrutor], [_tipologia(1)])

        primeira = metricas.oportunidades[0]
        assert 1 in primeira.instrutor_ids


class TestCapacidadeReposicao:
    def test_instrutor_com_sexta_disponivel_gera_horas_de_reposicao(self) -> None:
        instrutor = _instrutor(1, dias_semana=frozenset({2, 3, 4, 5, 6}))
        metricas, _, _ = _executar([instrutor], [_tipologia(1)])

        assert metricas.horas_reposicao_sexta > 0

    def test_instrutor_sem_sexta_nao_gera_reposicao(self) -> None:
        instrutor = _instrutor(1, dias_semana=frozenset({2, 3, 4, 5}))
        metricas, _, _ = _executar([instrutor], [_tipologia(1)])

        assert metricas.horas_reposicao_sexta == 0


class TestMetadados:
    def test_reune_totais_da_execucao(self) -> None:
        instrutor = _instrutor(1)
        metricas, resultado, _ = _executar([instrutor], [_tipologia(1)])

        assert metricas.metadados.total_turmas_sugeridas == len(resultado.candidatas_selecionadas)
        assert metricas.metadados.status_solver == resultado.status
        assert metricas.metadados.horas_formacao_total == sum(
            c.calendario.carga_horaria_total for c in resultado.candidatas_selecionadas
        )


class TestUtilizacaoPorInstrutor:
    def test_utilizacao_percentual_calculada_corretamente(self) -> None:
        instrutor = _instrutor(1, turnos={Turno.MANHA: 4.0})
        turma_andamento = TurmaAndamentoDados(
            instrutor_id=1,
            tipologia_id=1,
            modalidade=Modalidade.INTENSIVA_SEG_QUI,
            turno=Turno.MANHA,
            data_inicio=PERIODO_DE,
            data_fim_prevista=PERIODO_ATE,
        )
        metricas, _, _ = _executar(
            [instrutor], [_tipologia(1)], turmas_andamento=[turma_andamento]
        )

        utilizacao = metricas.utilizacao_por_instrutor[0]
        assert utilizacao.utilizacao_percentual == 100.0

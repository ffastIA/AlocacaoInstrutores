"""Testes do enumerador de turmas candidatas."""

from datetime import date, timedelta

from app.models.enums import Modalidade, Turno
from app.services.solver.gerador_candidatas import (
    InstrutorDados,
    TipologiaDados,
    TurmaAndamentoDados,
    gerar_candidatas,
)

PERIODO_DE = date(2026, 8, 31)  # segunda-feira
PERIODO_ATE = date(2027, 4, 30)


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


def _gerar(instrutores, tipologias, turmas_andamento=None, escopo=frozenset(), compartilhar=False):
    return gerar_candidatas(
        instrutores=instrutores,
        tipologias={t.id: t for t in tipologias},
        turmas_andamento=turmas_andamento or [],
        periodo_de=PERIODO_DE,
        periodo_ate=PERIODO_ATE,
        projetos_escopo=escopo,
        permitir_compartilhamento=compartilhar,
    )


class TestElegibilidadeBasica:
    def test_gera_candidatas_para_instrutor_apto(self) -> None:
        candidatas = _gerar([_instrutor(1)], [_tipologia(1)])

        assert len(candidatas) > 0
        assert all(c.instrutor_id == 1 and c.tipologia_id == 1 for c in candidatas)

    def test_tipologia_nao_dominada_nao_gera_candidata(self) -> None:
        """Instrutor apto a tipologia 1, mas o catálogo só define a tipologia 2."""
        candidatas = _gerar([_instrutor(1, tipologia_ids=frozenset({1}))], [_tipologia(2)])

        assert candidatas == []

    def test_tipologia_pendente_nao_gera_candidata(self) -> None:
        """Tipologia sem configuração (fora do dict de tipologias) não gera candidata."""
        candidatas = _gerar([_instrutor(1, tipologia_ids=frozenset({1, 2}))], [_tipologia(1)])

        assert all(c.tipologia_id == 1 for c in candidatas)

    def test_turno_indisponivel_nao_gera_candidata(self) -> None:
        instrutor = _instrutor(1, turnos={Turno.NOITE: 3.0})
        candidatas = _gerar([instrutor], [_tipologia(1)])

        assert all(c.turno == Turno.NOITE for c in candidatas)

    def test_instrutor_multi_tipologia_gera_candidatas_para_ambas(self) -> None:
        """Instrutor que domina Pixel Art e Programação gera oportunidades das duas."""
        instrutor = _instrutor(1, tipologia_ids=frozenset({1, 2}))
        candidatas = _gerar([instrutor], [_tipologia(1), _tipologia(2)])

        tipologias_geradas = {c.tipologia_id for c in candidatas}
        assert tipologias_geradas == {1, 2}


class TestPodaPorDias:
    def test_dias_incompativeis_com_modalidade_regular_seg_qua(self) -> None:
        """Instrutor disponível só terça/quinta não admite regular_seg_qua."""
        instrutor = _instrutor(1, dias_semana=frozenset({3, 5}))
        candidatas = _gerar([instrutor], [_tipologia(1)])

        modalidades = {c.modalidade for c in candidatas}
        assert Modalidade.REGULAR_SEG_QUA not in modalidades
        assert Modalidade.REGULAR_TER_QUI in modalidades

    def test_dias_incompativeis_com_intensiva(self) -> None:
        """Instrutor disponível só segunda/quarta não admite a intensiva (seg-qui)."""
        instrutor = _instrutor(1, dias_semana=frozenset({2, 4}))
        candidatas = _gerar([instrutor], [_tipologia(1)])

        assert Modalidade.INTENSIVA_SEG_QUI not in {c.modalidade for c in candidatas}
        assert Modalidade.REGULAR_SEG_QUA in {c.modalidade for c in candidatas}

    def test_disponibilidade_total_admite_as_tres_modalidades(self) -> None:
        instrutor = _instrutor(1, dias_semana=frozenset({2, 3, 4, 5}))
        candidatas = _gerar([instrutor], [_tipologia(1)])

        assert {c.modalidade for c in candidatas} == set(Modalidade)


class TestPodaPorCapacidadeDoTurno:
    def test_horas_por_encontro_acima_da_capacidade_do_turno(self) -> None:
        """Tipologia de 4h/encontro não cabe num turno de 3h."""
        instrutor = _instrutor(1, turnos={Turno.NOITE: 3.0})
        candidatas = _gerar([instrutor], [_tipologia(1, carga_total=40, horas_encontro=4)])

        assert candidatas == []

    def test_horas_por_encontro_igual_a_capacidade_e_aceita(self) -> None:
        instrutor = _instrutor(1, turnos={Turno.NOITE: 4.0})
        candidatas = _gerar([instrutor], [_tipologia(1, carga_total=40, horas_encontro=4)])

        assert len(candidatas) > 0


class TestPodaPorPeriodo:
    def test_turma_que_nao_cabe_no_periodo_nao_e_gerada(self) -> None:
        """Período de 1 semana não comporta uma turma de 10 encontros."""
        candidatas = gerar_candidatas(
            instrutores=[_instrutor(1)],
            tipologias={1: _tipologia(1)},
            turmas_andamento=[],
            periodo_de=PERIODO_DE,
            periodo_ate=PERIODO_DE + timedelta(days=6),
            projetos_escopo=frozenset(),
            permitir_compartilhamento=False,
        )

        assert candidatas == []

    def test_todas_as_candidatas_cabem_no_periodo(self) -> None:
        candidatas = _gerar([_instrutor(1)], [_tipologia(1)])

        assert all(c.calendario.data_inicio >= PERIODO_DE for c in candidatas)
        assert all(c.calendario.data_fim <= PERIODO_ATE for c in candidatas)


class TestOcupacaoPorTurmaAndamento:
    def test_candidata_que_colide_com_turma_em_andamento_e_podada(self) -> None:
        """Instrutor com turno lotado por turma em andamento não gera candidata ali."""
        instrutor = _instrutor(1, turnos={Turno.MANHA: 4.0})
        turma_andamento = TurmaAndamentoDados(
            instrutor_id=1,
            tipologia_id=1,
            modalidade=Modalidade.INTENSIVA_SEG_QUI,
            turno=Turno.MANHA,
            data_inicio=PERIODO_DE,
            data_fim_prevista=PERIODO_ATE,  # ocupa o turno o período inteiro
        )

        candidatas = _gerar([instrutor], [_tipologia(1)], turmas_andamento=[turma_andamento])

        assert candidatas == []

    def test_capacidade_residual_libera_outro_turno(self) -> None:
        """Turma em andamento pela manhã não impede candidata à tarde."""
        instrutor = _instrutor(1, turnos={Turno.MANHA: 4.0, Turno.TARDE: 4.0})
        turma_andamento = TurmaAndamentoDados(
            instrutor_id=1,
            tipologia_id=1,
            modalidade=Modalidade.INTENSIVA_SEG_QUI,
            turno=Turno.MANHA,
            data_inicio=PERIODO_DE,
            data_fim_prevista=PERIODO_ATE,
        )

        candidatas = _gerar([instrutor], [_tipologia(1)], turmas_andamento=[turma_andamento])

        assert candidatas, "deveria haver candidatas à tarde"
        assert all(c.turno == Turno.TARDE for c in candidatas)

    def test_capacidade_libera_apos_termino_da_turma_em_andamento(self) -> None:
        """Após a turma em andamento terminar, o turno volta a ficar disponível."""
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

        candidatas = _gerar([instrutor], [_tipologia(1)], turmas_andamento=[turma_andamento])

        assert candidatas, "deveria haver candidatas após o término"
        assert all(c.calendario.data_inicio > fim_turma for c in candidatas)

    def test_duas_tipologias_curtas_cabem_no_mesmo_turno(self) -> None:
        """Duas turmas de 2h cabem juntas num turno de 4h — não há colisão a priori."""
        instrutor = _instrutor(
            1, turnos={Turno.MANHA: 4.0}, tipologia_ids=frozenset({1, 2})
        )
        turma_andamento = TurmaAndamentoDados(
            instrutor_id=1,
            tipologia_id=1,
            modalidade=Modalidade.INTENSIVA_SEG_QUI,
            turno=Turno.MANHA,
            data_inicio=PERIODO_DE,
            data_fim_prevista=PERIODO_ATE,
        )
        # A ocupação usa 2h/encontro (tipologia 1), sobrando 2h no turno de 4h.
        candidatas = _gerar(
            [instrutor],
            [
                _tipologia(1, carga_total=24, horas_encontro=2),
                _tipologia(2, carga_total=24, horas_encontro=2),
            ],
            turmas_andamento=[turma_andamento],
        )

        assert candidatas, "deveria caber uma segunda turma de 2h no turno de 4h"


class TestCatalogoLimitadoAsHabilidades:
    def test_nenhuma_candidata_fora_da_uniao_de_habilidades_do_escopo(self) -> None:
        """Catálogo com 3 tipologias, mas só 2 são dominadas pelos instrutores do escopo."""
        instrutor_a = _instrutor(1, tipologia_ids=frozenset({1}))
        instrutor_b = _instrutor(2, tipologia_ids=frozenset({2}))
        # Tipologia 3 está configurada no catálogo, mas nenhum instrutor a domina.
        candidatas = _gerar(
            [instrutor_a, instrutor_b], [_tipologia(1), _tipologia(2), _tipologia(3)]
        )

        assert {c.tipologia_id for c in candidatas} == {1, 2}


class TestEscopoDeProjetos:
    def test_compartilhamento_desligado_restringe_ao_escopo(self) -> None:
        instrutor_dentro = _instrutor(1, projeto_id=1)
        instrutor_fora = _instrutor(2, projeto_id=2)

        candidatas = _gerar(
            [instrutor_dentro, instrutor_fora], [_tipologia(1)], escopo=frozenset({1})
        )

        assert all(c.instrutor_id == 1 for c in candidatas)

    def test_compartilhamento_ligado_ignora_o_escopo(self) -> None:
        instrutor_dentro = _instrutor(1, projeto_id=1)
        instrutor_fora = _instrutor(2, projeto_id=2)

        candidatas = _gerar(
            [instrutor_dentro, instrutor_fora],
            [_tipologia(1)],
            escopo=frozenset({1}),
            compartilhar=True,
        )

        assert {c.instrutor_id for c in candidatas} == {1, 2}

    def test_escopo_vazio_inclui_todos_os_projetos(self) -> None:
        instrutor_1 = _instrutor(1, projeto_id=1)
        instrutor_2 = _instrutor(2, projeto_id=2)

        candidatas = _gerar([instrutor_1, instrutor_2], [_tipologia(1)], escopo=frozenset())

        assert {c.instrutor_id for c in candidatas} == {1, 2}


class TestIdsSequenciais:
    def test_ids_sao_unicos_e_sequenciais(self) -> None:
        candidatas = _gerar([_instrutor(1)], [_tipologia(1)])

        ids = [c.id for c in candidatas]
        assert ids == list(range(len(candidatas)))

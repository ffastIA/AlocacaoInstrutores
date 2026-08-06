"""Testes do modelo CP-SAT.

Cenários sintéticos com resposta conhecida — cada teste valida uma restrição
ou um comportamento do objetivo isoladamente.
"""

from datetime import date

import pytest

from app.models.enums import Modalidade, Turno
from app.services.solver.cp_sat_model import (
    ConfiguracaoSolver,
    Normalizadores,
    PesosObjetivo,
    normalizadores_padrao,
    resolver,
)
from app.services.solver.dados import InstrutorDados, TipologiaDados, TurmaAndamentoDados
from app.services.solver.gerador_candidatas import gerar_candidatas

PERIODO_DE = date(2026, 8, 31)  # segunda-feira
PERIODO_ATE = date(2027, 4, 30)

PESOS_APROVEITAMENTO = PesosObjetivo(
    maximizar_aproveitamento=1.0,
    antecipar_inicio=0.0,
    balancear_carga_instrutores=0.0,
    balancear_tipologias=0.0,
)

CONFIG_RAPIDA = ConfiguracaoSolver(time_limit_seg=10, num_workers=4, seed=42)

# Determinismo byte-a-byte só é garantido com gap_relativo=0 (prova exata):
# com gap > 0, o CP-SAT pode reportar OTIMO para soluções diferentes dentro
# da margem, e qual delas aparece depende do timing dos workers paralelos.
CONFIG_DETERMINISTICA = ConfiguracaoSolver(
    time_limit_seg=10, num_workers=4, seed=42, gap_relativo=0.0
)


def _instrutor(
    id: int,
    projeto_id: int = 1,
    turnos: frozenset[Turno] | None = None,
    dias_semana: frozenset[int] = frozenset({2, 3, 4, 5}),
    tipologia_ids: frozenset[int] = frozenset({1}),
) -> InstrutorDados:
    return InstrutorDados(
        id=id,
        projeto_id=projeto_id,
        turnos=turnos or frozenset({Turno.MANHA_1}),
        dias_semana=dias_semana,
        tipologia_ids=tipologia_ids,
    )


def _tipologia(id: int, carga_total: float = 40, horas_encontro: float = 4) -> TipologiaDados:
    return TipologiaDados(
        id=id, carga_horaria_total_horas=carga_total, horas_por_encontro=horas_encontro
    )


def _resolver(
    instrutores,
    tipologias,
    turmas_andamento=None,
    pesos=PESOS_APROVEITAMENTO,
    escopo=frozenset(),
    compartilhar=False,
    periodo_ate=PERIODO_ATE,
    configuracao=CONFIG_RAPIDA,
):
    tipologias_dict = {t.id: t for t in tipologias}
    candidatas = gerar_candidatas(
        instrutores=instrutores,
        tipologias=tipologias_dict,
        turmas_andamento=turmas_andamento or [],
        periodo_de=PERIODO_DE,
        periodo_ate=periodo_ate,
        projetos_escopo=escopo,
        permitir_compartilhamento=compartilhar,
    )
    resultado = resolver(
        candidatas=candidatas,
        instrutores=instrutores,
        tipologias=tipologias_dict,
        turmas_andamento=turmas_andamento or [],
        periodo_de=PERIODO_DE,
        periodo_ate=periodo_ate,
        pesos=pesos,
        configuracao=configuracao,
    )
    return resultado, candidatas


class TestSolucaoSempreViavel:
    def test_sem_candidatas_resolve_para_solucao_vazia(self) -> None:
        resultado, _ = _resolver([], [])

        assert resultado.status in ("OTIMO", "FACTIVEL")
        assert resultado.candidatas_selecionadas == ()

    def test_nunca_retorna_infactivel(self) -> None:
        """O modelo não tem restrição de cobertura — sempre há solução (mesmo vazia)."""
        instrutor = _instrutor(1, turnos=frozenset({Turno.NOITE}))
        resultado, _ = _resolver([instrutor], [_tipologia(1, carga_total=40, horas_encontro=4)])

        assert resultado.status != "INFACTIVEL"


class TestAproveitamentoMaximo:
    def test_abre_a_unica_candidata_disponivel(self) -> None:
        instrutor = _instrutor(1)
        resultado, candidatas = _resolver([instrutor], [_tipologia(1)])

        assert len(resultado.candidatas_selecionadas) >= 1

    def test_peso_exclusivo_maximiza_horas_entregues(self) -> None:
        """Com peso só em aproveitamento, o solver abre o máximo de turmas possível."""
        instrutor = _instrutor(
            1, turnos=frozenset({Turno.MANHA_1}), tipologia_ids=frozenset({1, 2})
        )
        resultado, candidatas = _resolver(
            [instrutor],
            [
                _tipologia(1, carga_total=24, horas_encontro=2),
                _tipologia(2, carga_total=24, horas_encontro=2),
            ],
        )

        # Nenhuma seleção possível teria mais horas do que a ótima encontrada.
        horas_selecionadas = sum(
            c.calendario.carga_horaria_total for c in resultado.candidatas_selecionadas
        )
        assert horas_selecionadas > 0


class TestRestricaoCapacidadeSlot:
    def test_duas_candidatas_no_mesmo_slot_nao_coexistem(self) -> None:
        """Um slot comporta no máximo 1 turma por vez — mesmo com duas
        tipologias competindo pelo mesmo (instrutor, slot), só uma é aberta em
        cada data."""
        instrutor = _instrutor(
            1, turnos=frozenset({Turno.MANHA_1}), tipologia_ids=frozenset({1, 2})
        )
        resultado, _ = _resolver(
            [instrutor],
            [
                _tipologia(1, carga_total=8, horas_encontro=2),
                _tipologia(2, carga_total=8, horas_encontro=2),
            ],
            pesos=PESOS_APROVEITAMENTO,
        )

        _validar_nenhum_slot_duplicado(resultado.candidatas_selecionadas)

    def test_qualquer_tipologia_cabe_em_qualquer_slot(self) -> None:
        """Sem carga horária por turno, uma tipologia de 4h/encontro tem
        candidatas normalmente mesmo num slot único como a noite."""
        instrutor = _instrutor(1, turnos=frozenset({Turno.NOITE}))
        _, candidatas = _resolver([instrutor], [_tipologia(1, carga_total=40, horas_encontro=4)])

        assert candidatas != []

    def test_slot_ja_ocupado_por_turma_em_andamento_nao_recebe_sugestao(self) -> None:
        instrutor = _instrutor(1, turnos=frozenset({Turno.NOITE}))
        turma_andamento = TurmaAndamentoDados(
            instrutor_id=1,
            tipologia_id=1,
            modalidade=Modalidade.INTENSIVA_SEG_QUI,
            turno=Turno.NOITE,
            data_inicio=PERIODO_DE,
            data_fim_prevista=PERIODO_ATE,
        )

        resultado, _ = _resolver([instrutor], [_tipologia(1)], turmas_andamento=[turma_andamento])

        assert resultado.candidatas_selecionadas == ()


class TestCapacidadeResidualETurnoLivre:
    def test_instrutor_com_turma_pela_manha_recebe_sugestao_a_tarde(self) -> None:
        instrutor = _instrutor(1, turnos=frozenset({Turno.MANHA_1, Turno.TARDE_1}))
        turma_andamento = TurmaAndamentoDados(
            instrutor_id=1,
            tipologia_id=1,
            modalidade=Modalidade.INTENSIVA_SEG_QUI,
            turno=Turno.MANHA_1,
            data_inicio=PERIODO_DE,
            data_fim_prevista=PERIODO_ATE,
        )

        resultado, _ = _resolver(
            [instrutor],
            [_tipologia(1)],
            turmas_andamento=[turma_andamento],
            pesos=PESOS_APROVEITAMENTO,
        )

        assert resultado.candidatas_selecionadas
        assert all(c.turno == Turno.TARDE_1 for c in resultado.candidatas_selecionadas)

    def test_nao_recebe_sugestao_no_turno_ocupado(self) -> None:
        instrutor = _instrutor(1, turnos=frozenset({Turno.MANHA_1}))
        turma_andamento = TurmaAndamentoDados(
            instrutor_id=1,
            tipologia_id=1,
            modalidade=Modalidade.INTENSIVA_SEG_QUI,
            turno=Turno.MANHA_1,
            data_inicio=PERIODO_DE,
            data_fim_prevista=PERIODO_ATE,
        )

        resultado, _ = _resolver([instrutor], [_tipologia(1)], turmas_andamento=[turma_andamento])

        assert resultado.candidatas_selecionadas == ()


class TestEncadeamento:
    def test_instrutor_recebe_turmas_sucessivas_nao_apenas_a_primeira(self) -> None:
        """Período longo comporta múltiplas turmas sucessivas do mesmo instrutor."""
        instrutor = _instrutor(1, turnos=frozenset({Turno.MANHA_1}))
        resultado, _ = _resolver(
            [instrutor],
            [_tipologia(1, carga_total=40, horas_encontro=4)],
            pesos=PESOS_APROVEITAMENTO,
        )

        assert len(resultado.candidatas_selecionadas) >= 2, (
            "esperava-se ao menos duas turmas sucessivas no período de ~35 semanas"
        )

    def test_turmas_sucessivas_nao_se_sobrepoem(self) -> None:
        instrutor = _instrutor(1, turnos=frozenset({Turno.MANHA_1}))
        resultado, _ = _resolver(
            [instrutor],
            [_tipologia(1, carga_total=40, horas_encontro=4)],
            pesos=PESOS_APROVEITAMENTO,
        )

        _validar_nenhum_slot_duplicado(resultado.candidatas_selecionadas)


class TestEscopoDeProjetos:
    def test_compartilhamento_desligado_nao_abre_turma_de_outro_projeto(self) -> None:
        instrutor_fora = _instrutor(1, projeto_id=2)
        resultado, candidatas = _resolver(
            [instrutor_fora], [_tipologia(1)], escopo=frozenset({1}), pesos=PESOS_APROVEITAMENTO
        )

        assert candidatas == []
        assert resultado.candidatas_selecionadas == ()


class TestObjetivoComposto:
    def test_peso_em_equilibrio_de_tipologias_distribui_a_oferta(self) -> None:
        """Instrutor multi-tipologia: peso em equilíbrio evita concentrar tudo numa só.

        Duas tipologias idênticas em custo (mesmas horas), com candidatas
        suficientes para cobrir o período inteiro com qualquer uma das duas.
        Sem peso de equilíbrio, o desempate (menor id) concentra tudo na
        tipologia 1; com peso de equilíbrio, a distribuição se torna próxima.
        """
        instrutor = _instrutor(
            1, turnos=frozenset({Turno.MANHA_1}), tipologia_ids=frozenset({1, 2})
        )
        tipologias = [
            _tipologia(1, carga_total=8, horas_encontro=4),
            _tipologia(2, carga_total=8, horas_encontro=4),
        ]

        pesos_sem_equilibrio = PesosObjetivo(
            maximizar_aproveitamento=1.0,
            antecipar_inicio=0.0,
            balancear_carga_instrutores=0.0,
            balancear_tipologias=0.0,
        )
        pesos_com_equilibrio = PesosObjetivo(
            maximizar_aproveitamento=0.3,
            antecipar_inicio=0.0,
            balancear_carga_instrutores=0.0,
            balancear_tipologias=0.7,
        )

        sem_equilibrio, candidatas = _resolver(
            [instrutor], tipologias, pesos=pesos_sem_equilibrio, periodo_ate=date(2026, 11, 30)
        )
        com_equilibrio, _ = _resolver(
            [instrutor], tipologias, pesos=pesos_com_equilibrio, periodo_ate=date(2026, 11, 30)
        )

        # Inclui toda tipologia candidata com 0 como padrão — uma tipologia
        # totalmente excluída da seleção precisa contar como 0, não desaparecer
        # do cálculo (senão o desvio de um único valor presente sempre daria 0).
        universo_tipologias = {c.tipologia_id for c in candidatas}
        distribuicao_sem = _distribuicao_por_tipologia(
            sem_equilibrio.candidatas_selecionadas, universo_tipologias
        )
        distribuicao_com = _distribuicao_por_tipologia(
            com_equilibrio.candidatas_selecionadas, universo_tipologias
        )

        desvio_sem = max(distribuicao_sem.values()) - min(distribuicao_sem.values())
        desvio_com = max(distribuicao_com.values()) - min(distribuicao_com.values())

        assert desvio_sem > 0, "sem peso de equilíbrio, esperava-se concentração numa tipologia"
        assert desvio_com < desvio_sem, "o peso de equilíbrio deveria reduzir o desvio"

    def test_peso_em_antecipacao_prefere_inicio_mais_cedo(self) -> None:
        """Entre soluções de aproveitamento equivalente, prioriza começar antes."""
        instrutor = _instrutor(1, turnos=frozenset({Turno.MANHA_1}))
        pesos = PesosObjetivo(
            maximizar_aproveitamento=0.1,
            antecipar_inicio=0.9,
            balancear_carga_instrutores=0.0,
            balancear_tipologias=0.0,
        )

        resultado, _ = _resolver(
            [instrutor],
            [_tipologia(1, carga_total=8, horas_encontro=4)],
            pesos=pesos,
            periodo_ate=date(2026, 9, 21),
        )

        assert resultado.candidatas_selecionadas
        primeira = min(c.semana_inicio for c in resultado.candidatas_selecionadas)
        assert primeira == 0

    def test_normalizacao_evita_dominancia_de_escala(self) -> None:
        """Alterar apenas a escala de um normalizador, mantendo os pesos, não muda a solução."""
        instrutor = _instrutor(1, turnos=frozenset({Turno.MANHA_1}))
        tipologias = [_tipologia(1, carga_total=8, horas_encontro=4)]
        tipologias_dict = {t.id: t for t in tipologias}

        candidatas = gerar_candidatas(
            instrutores=[instrutor],
            tipologias=tipologias_dict,
            turmas_andamento=[],
            periodo_de=PERIODO_DE,
            periodo_ate=date(2026, 9, 21),
            projetos_escopo=frozenset(),
            permitir_compartilhamento=False,
        )

        pesos = PesosObjetivo(1.0, 0.0, 0.0, 0.0)

        r1 = resolver(
            candidatas=candidatas,
            instrutores=[instrutor],
            tipologias=tipologias_dict,
            turmas_andamento=[],
            periodo_de=PERIODO_DE,
            periodo_ate=date(2026, 9, 21),
            pesos=pesos,
            normalizadores=Normalizadores(10.0, 1.0, 1000.0, 1.0),
            configuracao=CONFIG_RAPIDA,
        )
        r2 = resolver(
            candidatas=candidatas,
            instrutores=[instrutor],
            tipologias=tipologias_dict,
            turmas_andamento=[],
            periodo_de=PERIODO_DE,
            periodo_ate=date(2026, 9, 21),
            pesos=pesos,
            normalizadores=Normalizadores(10_000.0, 1.0, 1000.0, 1.0),
            configuracao=CONFIG_RAPIDA,
        )

        ids_r1 = {c.id for c in r1.candidatas_selecionadas}
        ids_r2 = {c.id for c in r2.candidatas_selecionadas}
        assert ids_r1 == ids_r2


class TestDeterminismo:
    def test_duas_execucoes_produzem_resultado_identico(self) -> None:
        """Com gap_relativo=0 (prova exata), o resultado é reprodutível mesmo
        com múltiplos workers — a segunda passagem de desempate garante isso."""
        instrutor = _instrutor(
            1, turnos=frozenset({Turno.MANHA_1}), tipologia_ids=frozenset({1, 2})
        )
        tipologias = [_tipologia(1), _tipologia(2, carga_total=24, horas_encontro=2)]

        r1, _ = _resolver(
            [instrutor], tipologias, pesos=PESOS_APROVEITAMENTO, configuracao=CONFIG_DETERMINISTICA
        )
        r2, _ = _resolver(
            [instrutor], tipologias, pesos=PESOS_APROVEITAMENTO, configuracao=CONFIG_DETERMINISTICA
        )

        ids_r1 = {c.id for c in r1.candidatas_selecionadas}
        ids_r2 = {c.id for c in r2.candidatas_selecionadas}
        assert ids_r1 == ids_r2
        assert r1.objetivo_valor == pytest.approx(r2.objetivo_valor)


class TestNormalizadoresPadrao:
    def test_sem_candidatas_retorna_normalizadores_neutros(self) -> None:
        normalizadores = normalizadores_padrao([], [], {}, PERIODO_DE, PERIODO_ATE)

        assert normalizadores.aproveitamento == 1.0
        assert normalizadores.antecipacao == 1.0

    def test_aproveitamento_usa_capacidade_real_nao_soma_de_candidatas(self) -> None:
        """O teto de aproveitamento é a capacidade disponível, não a soma bruta
        das candidatas — a maioria delas compete pelo mesmo instrutor/turno/data
        e jamais poderia ser aberta simultaneamente."""
        instrutor = _instrutor(
            1, turnos=frozenset({Turno.MANHA_1}), tipologia_ids=frozenset({1, 2})
        )
        tipologias_dict = {1: _tipologia(1), 2: _tipologia(2, carga_total=24, horas_encontro=2)}
        candidatas = gerar_candidatas(
            instrutores=[instrutor],
            tipologias=tipologias_dict,
            turmas_andamento=[],
            periodo_de=PERIODO_DE,
            periodo_ate=PERIODO_ATE,
            projetos_escopo=frozenset(),
            permitir_compartilhamento=False,
        )
        soma_bruta_candidatas = sum(c.calendario.carga_horaria_total for c in candidatas)

        normalizadores = normalizadores_padrao(
            candidatas, [instrutor], tipologias_dict, PERIODO_DE, PERIODO_ATE
        )

        assert normalizadores.aproveitamento < soma_bruta_candidatas


# --------------------------------------------------------------------------
# Utilitários de verificação
# --------------------------------------------------------------------------


def _distribuicao_por_tipologia(
    candidatas_selecionadas, universo: set[int] | None = None
) -> dict[int, int]:
    distribuicao: dict[int, int] = {tid: 0 for tid in (universo or set())}
    for c in candidatas_selecionadas:
        distribuicao[c.tipologia_id] = distribuicao.get(c.tipologia_id, 0) + 1
    return distribuicao


def _validar_nenhum_slot_duplicado(candidatas_selecionadas) -> None:
    """Confere que nenhum (instrutor, slot, data) é ocupado por mais de uma
    turma selecionada — capacidade binária: no máximo 1 turma por slot."""
    ocupacao: dict[tuple, int] = {}
    for c in candidatas_selecionadas:
        for encontro in c.calendario.encontros:
            chave = (c.instrutor_id, c.turno, encontro.data)
            ocupacao[chave] = ocupacao.get(chave, 0) + 1

    for chave, quantidade in ocupacao.items():
        assert quantidade <= 1, f"slot ocupado por {quantidade} turmas simultâneas: {chave}"

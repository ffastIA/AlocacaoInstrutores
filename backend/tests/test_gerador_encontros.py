"""Testes do gerador de calendário de encontros."""

from datetime import date

import pytest

from app.models.enums import Modalidade, Turno
from app.services.calendario.gerador_encontros import (
    duracao_em_semanas,
    gerar_calendario,
    segunda_feira_da_semana,
)

# Uma segunda-feira real, para servir de referência nos testes.
SEGUNDA_REFERENCIA = date(2026, 8, 3)


class TestSegundaFeiraDaSemana:
    def test_semana_zero_e_a_propria_semana_da_referencia(self) -> None:
        assert segunda_feira_da_semana(SEGUNDA_REFERENCIA, 0) == SEGUNDA_REFERENCIA

    def test_referencia_no_meio_da_semana(self) -> None:
        quarta = date(2026, 8, 5)
        assert segunda_feira_da_semana(quarta, 0) == SEGUNDA_REFERENCIA

    def test_deslocamento_positivo(self) -> None:
        assert segunda_feira_da_semana(SEGUNDA_REFERENCIA, 2) == date(2026, 8, 17)


class TestGerarCalendarioRegular:
    def test_numero_de_encontros(self) -> None:
        """40h com 4h por encontro = 10 encontros."""
        calendario = gerar_calendario(
            data_referencia=SEGUNDA_REFERENCIA,
            semana_inicio=0,
            modalidade=Modalidade.REGULAR_SEG_QUA,
            turno=Turno.MANHA_1,
            carga_horaria_total_horas=40,
            horas_por_encontro=4,
        )

        assert calendario.num_encontros == 10

    def test_dias_intercalados_segunda_quarta(self) -> None:
        calendario = gerar_calendario(
            data_referencia=SEGUNDA_REFERENCIA,
            semana_inicio=0,
            modalidade=Modalidade.REGULAR_SEG_QUA,
            turno=Turno.MANHA_1,
            carga_horaria_total_horas=8,
            horas_por_encontro=4,
        )

        assert [e.data.isoweekday() for e in calendario.encontros] == [1, 3]  # seg, qua

    def test_dias_intercalados_terca_quinta(self) -> None:
        calendario = gerar_calendario(
            data_referencia=SEGUNDA_REFERENCIA,
            semana_inicio=0,
            modalidade=Modalidade.REGULAR_TER_QUI,
            turno=Turno.MANHA_1,
            carga_horaria_total_horas=8,
            horas_por_encontro=4,
        )

        assert [e.data.isoweekday() for e in calendario.encontros] == [2, 4]  # ter, qui

    def test_carga_horaria_preservada(self) -> None:
        calendario = gerar_calendario(
            data_referencia=SEGUNDA_REFERENCIA,
            semana_inicio=0,
            modalidade=Modalidade.REGULAR_SEG_QUA,
            turno=Turno.MANHA_1,
            carga_horaria_total_horas=24,
            horas_por_encontro=2,
        )

        assert calendario.carga_horaria_total == 24

    def test_data_termino_e_do_ultimo_encontro(self) -> None:
        calendario = gerar_calendario(
            data_referencia=SEGUNDA_REFERENCIA,
            semana_inicio=0,
            modalidade=Modalidade.REGULAR_SEG_QUA,
            turno=Turno.MANHA_1,
            carga_horaria_total_horas=8,
            horas_por_encontro=4,
        )

        assert calendario.data_fim == calendario.encontros[-1].data


class TestGerarCalendarioIntensiva:
    def test_dias_segunda_a_quinta(self) -> None:
        calendario = gerar_calendario(
            data_referencia=SEGUNDA_REFERENCIA,
            semana_inicio=0,
            modalidade=Modalidade.INTENSIVA_SEG_QUI,
            turno=Turno.NOITE,
            carga_horaria_total_horas=12,
            horas_por_encontro=3,
        )

        assert [e.data.isoweekday() for e in calendario.encontros] == [1, 2, 3, 4]

    def test_termina_mais_cedo_que_a_modalidade_regular(self) -> None:
        """Mesma tipologia, mesma semana de início: intensiva conclui antes."""
        comum = dict(
            data_referencia=SEGUNDA_REFERENCIA,
            semana_inicio=0,
            turno=Turno.NOITE,
            carga_horaria_total_horas=40,
            horas_por_encontro=4,
        )

        regular = gerar_calendario(modalidade=Modalidade.REGULAR_SEG_QUA, **comum)
        intensiva = gerar_calendario(modalidade=Modalidade.INTENSIVA_SEG_QUI, **comum)

        assert intensiva.data_fim < regular.data_fim


class TestAusenciaDeSexta:
    @pytest.mark.parametrize("modalidade", list(Modalidade))
    @pytest.mark.parametrize("semana_inicio", range(8))
    def test_nenhum_encontro_cai_em_sexta(
        self, modalidade: Modalidade, semana_inicio: int
    ) -> None:
        calendario = gerar_calendario(
            data_referencia=SEGUNDA_REFERENCIA,
            semana_inicio=semana_inicio,
            modalidade=modalidade,
            turno=Turno.MANHA_1,
            carga_horaria_total_horas=48,
            horas_por_encontro=4,
        )

        dias_semana = {e.data.isoweekday() for e in calendario.encontros}
        assert 5 not in dias_semana  # 5 = sexta no padrão ISO


class TestDeterminismo:
    def test_mesmos_parametros_produzem_mesmo_resultado(self) -> None:
        parametros = dict(
            data_referencia=SEGUNDA_REFERENCIA,
            semana_inicio=3,
            modalidade=Modalidade.INTENSIVA_SEG_QUI,
            turno=Turno.TARDE_1,
            carga_horaria_total_horas=24,
            horas_por_encontro=2,
        )

        primeiro = gerar_calendario(**parametros)
        segundo = gerar_calendario(**parametros)

        assert primeiro == segundo


class TestCargaInvalida:
    def test_carga_nao_divisivel_e_rejeitada(self) -> None:
        with pytest.raises(ValueError, match="múltiplo exato"):
            gerar_calendario(
                data_referencia=SEGUNDA_REFERENCIA,
                semana_inicio=0,
                modalidade=Modalidade.REGULAR_SEG_QUA,
                turno=Turno.MANHA_1,
                carga_horaria_total_horas=50,
                horas_por_encontro=4,
            )


class TestHorasPorSemana:
    def test_semana_de_borda_soma_menos_que_semana_cheia(self) -> None:
        """Turma iniciando na quarta-feira: a 1ª semana tem só 1 encontro."""
        segunda_semana_0 = SEGUNDA_REFERENCIA
        calendario = gerar_calendario(
            data_referencia=SEGUNDA_REFERENCIA,
            semana_inicio=0,
            modalidade=Modalidade.INTENSIVA_SEG_QUI,
            turno=Turno.MANHA_1,
            carga_horaria_total_horas=24,
            horas_por_encontro=3,
        )

        horas = calendario.horas_por_semana(segunda_semana_0)
        assert sum(horas.values()) == 24


class TestDuracaoEmSemanas:
    def test_encontros_cabem_exatamente(self) -> None:
        """4 encontros intensivos (4/semana) cabem em exatamente 1 semana."""
        assert duracao_em_semanas(Modalidade.INTENSIVA_SEG_QUI, 4) == 1

    def test_encontros_com_semana_parcial(self) -> None:
        """5 encontros regulares (2/semana): 2 semanas cheias + 1 parcial."""
        assert duracao_em_semanas(Modalidade.REGULAR_SEG_QUA, 5) == 3

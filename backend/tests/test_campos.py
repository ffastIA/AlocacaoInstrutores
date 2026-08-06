"""Testes da interpretação dos campos multivalorados."""

import pytest

from app.models.enums import Turno
from app.services.importacao.campos import (
    ValorInvalidoError,
    parse_data,
    parse_dias_semana,
    parse_lista,
    parse_turno,
    parse_turnos,
)
from app.services.importacao.leitor_planilha import normalizar_cabecalho


class TestNormalizarCabecalho:
    @pytest.mark.parametrize(
        ("entrada", "esperado"),
        [
            ("Nome", "nome"),
            ("Dias Semana", "dias_semana"),
            ("DIAS SEMANA", "dias_semana"),
            ("Carga Horária Turno", "carga_horaria_turno"),
            ("  Tipologias  ", "tipologias"),
            ("Data-Início", "data_inicio"),
            ("Código  Turma", "codigo_turma"),
        ],
    )
    def test_normaliza(self, entrada: str, esperado: str) -> None:
        assert normalizar_cabecalho(entrada) == esperado


class TestParseLista:
    def test_divide_por_ponto_e_virgula(self) -> None:
        assert parse_lista("Programação;Pixel Art") == ["Programação", "Pixel Art"]

    def test_remove_espacos_das_extremidades(self) -> None:
        assert parse_lista("Programação ; Pixel Art") == ["Programação", "Pixel Art"]

    def test_descarta_itens_vazios(self) -> None:
        assert parse_lista("manha;;tarde;") == ["manha", "tarde"]

    def test_texto_vazio_gera_lista_vazia(self) -> None:
        assert parse_lista("") == []


class TestParseTurnos:
    def test_multiplos_slots(self) -> None:
        assert parse_turnos("manha_1;noite") == [Turno.MANHA_1, Turno.NOITE]

    def test_turno_unico(self) -> None:
        assert parse_turnos("noite") == [Turno.NOITE]

    def test_aceita_acento_e_maiuscula(self) -> None:
        assert parse_turnos("Manhã_1;Tarde_1") == [Turno.MANHA_1, Turno.TARDE_1]

    def test_turno_invalido_e_rejeitado(self) -> None:
        with pytest.raises(ValorInvalidoError, match="Turno inválido"):
            parse_turnos("madrugada")

    def test_turno_sem_slot_e_rejeitado(self) -> None:
        """O valor antigo 'manha' (sem slot) não é mais aceito."""
        with pytest.raises(ValorInvalidoError, match="Turno inválido"):
            parse_turnos("manha")

    def test_turno_duplicado_e_rejeitado(self) -> None:
        with pytest.raises(ValorInvalidoError, match="mais de uma vez"):
            parse_turnos("manha_1;manha_1")

    def test_turnos_vazios_sao_rejeitados(self) -> None:
        with pytest.raises(ValorInvalidoError, match="Nenhum turno"):
            parse_turnos("")


class TestParseTurno:
    @pytest.mark.parametrize(
        ("entrada", "esperado"),
        [("manha_1", Turno.MANHA_1), ("Manhã_2", Turno.MANHA_2), ("NOITE", Turno.NOITE)],
    )
    def test_interpreta(self, entrada: str, esperado: Turno) -> None:
        assert parse_turno(entrada) == esperado


class TestParseDiasSemana:
    def test_dias_intercalados(self) -> None:
        assert parse_dias_semana("2;4") == [2, 4]

    def test_ordena_o_resultado(self) -> None:
        assert parse_dias_semana("5;2;3") == [2, 3, 5]

    def test_aceita_sexta_como_reposicao(self) -> None:
        """O dia 6 é armazenado, mas nunca recebe turma regular."""
        assert parse_dias_semana("2;3;4;5;6") == [2, 3, 4, 5, 6]

    def test_dia_fora_da_faixa_e_rejeitado(self) -> None:
        with pytest.raises(ValorInvalidoError, match="fora da faixa"):
            parse_dias_semana("2;7")

    def test_domingo_e_rejeitado(self) -> None:
        with pytest.raises(ValorInvalidoError, match="fora da faixa"):
            parse_dias_semana("1")

    def test_dia_nao_numerico_e_rejeitado(self) -> None:
        with pytest.raises(ValorInvalidoError, match="inválido"):
            parse_dias_semana("segunda")

    def test_dia_duplicado_e_rejeitado(self) -> None:
        with pytest.raises(ValorInvalidoError, match="mais de uma vez"):
            parse_dias_semana("2;2")


class TestParseData:
    def test_formato_brasileiro(self) -> None:
        assert parse_data("30/08/2026").isoformat() == "2026-08-30"

    def test_formato_iso(self) -> None:
        assert parse_data("2026-08-30").isoformat() == "2026-08-30"

    def test_data_invalida_e_rejeitada(self) -> None:
        with pytest.raises(ValorInvalidoError, match="DD/MM/AAAA"):
            parse_data("31/02/2026")

    def test_texto_nao_data_e_rejeitado(self) -> None:
        with pytest.raises(ValorInvalidoError, match="inválida"):
            parse_data("ontem")

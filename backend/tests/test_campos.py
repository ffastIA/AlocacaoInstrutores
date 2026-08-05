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
    def test_formato_posicional(self) -> None:
        assert parse_turnos("manha;noite", "4;3") == [(Turno.MANHA, 4.0), (Turno.NOITE, 3.0)]

    def test_formato_explicito_dispensa_coluna_de_carga(self) -> None:
        assert parse_turnos("manha:4;tarde:4", "") == [(Turno.MANHA, 4.0), (Turno.TARDE, 4.0)]

    def test_turno_unico(self) -> None:
        assert parse_turnos("noite", "3") == [(Turno.NOITE, 3.0)]

    def test_aceita_acento_e_maiuscula(self) -> None:
        assert parse_turnos("Manhã;Tarde", "4;4") == [(Turno.MANHA, 4.0), (Turno.TARDE, 4.0)]

    def test_aceita_virgula_decimal(self) -> None:
        assert parse_turnos("manha", "3,5") == [(Turno.MANHA, 3.5)]

    def test_listas_de_tamanhos_diferentes_sao_rejeitadas(self) -> None:
        """Inferir a carga faltante produziria capacidade errada sem sinal visível."""
        with pytest.raises(ValorInvalidoError, match="mesma quantidade"):
            parse_turnos("manha;tarde", "4")

    def test_carga_ausente_no_formato_posicional_e_rejeitada(self) -> None:
        with pytest.raises(ValorInvalidoError, match="não informada"):
            parse_turnos("manha;tarde", "")

    def test_turno_invalido_e_rejeitado(self) -> None:
        with pytest.raises(ValorInvalidoError, match="Turno inválido"):
            parse_turnos("madrugada", "4")

    def test_carga_zero_e_rejeitada(self) -> None:
        with pytest.raises(ValorInvalidoError, match="maior que zero"):
            parse_turnos("manha", "0")

    def test_turno_duplicado_e_rejeitado(self) -> None:
        with pytest.raises(ValorInvalidoError, match="mais de uma vez"):
            parse_turnos("manha;manha", "4;3")

    def test_turnos_vazios_sao_rejeitados(self) -> None:
        with pytest.raises(ValorInvalidoError, match="Nenhum turno"):
            parse_turnos("", "4")


class TestParseTurno:
    @pytest.mark.parametrize(
        ("entrada", "esperado"),
        [("manha", Turno.MANHA), ("Manhã", Turno.MANHA), ("NOITE", Turno.NOITE)],
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

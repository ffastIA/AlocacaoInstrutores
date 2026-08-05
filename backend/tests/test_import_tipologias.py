"""Testes da importação da planilha de tipologias."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Tipologia
from app.services.importacao.parser_instrutores import importar_instrutores
from app.services.importacao.parser_tipologias import importar_tipologias, listar_pendentes
from tests.fabricas import planilha_instrutores, planilha_tipologias


def _importar(db: Session, linhas: list[list[str]]):
    return importar_tipologias(db, planilha_tipologias(linhas), "tipologias.csv")


def _criar_instrutor_com(db: Session, tipologias: str) -> None:
    importar_instrutores(
        db,
        planilha_instrutores([["Maria Silva", "Jovem Digital", "manha", "4", "2;4", tipologias]]),
        "instrutores.csv",
    )


class TestConfiguracao:
    def test_configura_tipologia_derivada(self, db: Session) -> None:
        _criar_instrutor_com(db, "Robótica")

        resultado = _importar(db, [["Robótica", "40", "4"]])

        assert resultado.erros == []
        tipologia = db.scalar(select(Tipologia).where(Tipologia.nome == "Robótica"))
        assert tipologia.carga_horaria_total_horas == 40
        assert tipologia.horas_por_encontro == 4
        assert tipologia.configurada is True
        assert tipologia.num_encontros == 10

    def test_remove_a_pendencia(self, db: Session) -> None:
        _criar_instrutor_com(db, "Robótica")
        assert len(listar_pendentes(db)) == 1

        _importar(db, [["Robótica", "40", "4"]])

        assert listar_pendentes(db) == []

    def test_configura_varias_tipologias(self, db: Session) -> None:
        _criar_instrutor_com(db, "Programação;Pixel Art;Robótica")

        resultado = _importar(
            db, [["Programação", "60", "3"], ["Pixel Art", "24", "2"], ["Robótica", "40", "4"]]
        )

        assert resultado.erros == []
        assert listar_pendentes(db) == []


class TestValidacao:
    def test_rejeita_carga_nao_divisivel(self, db: Session) -> None:
        """50h com 4h por encontro daria 12,5 encontros."""
        _criar_instrutor_com(db, "Robótica")

        resultado = _importar(db, [["Robótica", "50", "4"]])

        assert "múltiplo exato" in resultado.erros[0].motivo
        tipologia = db.scalar(select(Tipologia).where(Tipologia.nome == "Robótica"))
        assert tipologia.configurada is False

    def test_rejeita_carga_acima_do_limite(self, db: Session) -> None:
        _criar_instrutor_com(db, "Robótica")

        resultado = _importar(db, [["Robótica", "80", "4"]])

        assert "fora da faixa" in resultado.erros[0].motivo

    def test_rejeita_carga_abaixo_do_limite(self, db: Session) -> None:
        _criar_instrutor_com(db, "Robótica")

        resultado = _importar(db, [["Robótica", "12", "2"]])

        assert "fora da faixa" in resultado.erros[0].motivo

    def test_rejeita_valor_nao_numerico(self, db: Session) -> None:
        _criar_instrutor_com(db, "Robótica")

        resultado = _importar(db, [["Robótica", "quarenta", "4"]])

        assert "inválido" in resultado.erros[0].motivo

    def test_importa_validas_e_reporta_invalidas(self, db: Session) -> None:
        _criar_instrutor_com(db, "Programação;Robótica")

        resultado = _importar(db, [["Programação", "60", "3"], ["Robótica", "50", "4"]])

        assert resultado.atualizados == 1
        assert len(resultado.erros) == 1
        assert listar_pendentes(db)[0].nome == "Robótica"


class TestTipologiaOrfa:
    def test_alerta_para_tipologia_sem_instrutor(self, db: Session) -> None:
        """Aceita, mas avisa: sem instrutor apto, nunca será ofertada."""
        resultado = _importar(db, [["Xadrez", "24", "2"]])

        assert resultado.erros == []
        assert any("nenhum instrutor" in a.mensagem for a in resultado.alertas)

    def test_nao_alerta_quando_ha_instrutor(self, db: Session) -> None:
        _criar_instrutor_com(db, "Robótica")

        resultado = _importar(db, [["Robótica", "40", "4"]])

        assert not any("nenhum instrutor" in a.mensagem for a in resultado.alertas)


class TestArquivoRecusado:
    def test_coluna_obrigatoria_ausente(self, db: Session) -> None:
        from tests.fabricas import csv_bytes

        conteudo = csv_bytes(["tipologia", "carga_horaria_total"], [["Robótica", "40"]])

        resultado = importar_tipologias(db, conteudo, "tipologias.csv")

        assert resultado.erro_arquivo is not None
        assert "horas_por_encontro" in resultado.erro_arquivo

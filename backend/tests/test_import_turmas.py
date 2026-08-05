"""Testes da importação das turmas em andamento."""

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Modalidade, TurmaEmAndamento, Turno
from app.services.importacao.parser_instrutores import importar_instrutores
from app.services.importacao.parser_tipologias import importar_tipologias
from app.services.importacao.parser_turmas_andamento import importar_turmas_andamento
from tests.fabricas import planilha_instrutores, planilha_tipologias, planilha_turmas


@pytest.fixture
def base_carregada(db: Session) -> Session:
    """Instrutores e tipologias já configurados, prontos para receber turmas."""
    importar_instrutores(
        db,
        planilha_instrutores(
            [
                ["Maria Silva", "Jovem Digital", "manha;tarde", "4;4", "2;3;4;5",
                 "Programação;Pixel Art"],
                ["João Souza", "Jovem Digital", "noite", "3", "2;3;4;5", "Robótica"],
            ]
        ),
        "instrutores.csv",
    )
    importar_tipologias(
        db,
        planilha_tipologias(
            [["Programação", "60", "3"], ["Pixel Art", "24", "2"], ["Robótica", "40", "4"]]
        ),
        "tipologias.csv",
    )
    return db


def _importar(db: Session, linhas: list[list[str]]):
    return importar_turmas_andamento(db, planilha_turmas(linhas), "turmas.csv")


class TestImportacaoBemSucedida:
    def test_importa_turmas(self, base_carregada: Session) -> None:
        resultado = _importar(
            base_carregada,
            [
                ["Maria Silva", "Programação", "regular_seg_qua", "manha",
                 "01/06/2026", "30/08/2026"],
                ["João Souza", "Robótica", "intensiva_seg_qui", "noite",
                 "15/07/2026", "20/09/2026"],
            ],
        )

        assert resultado.erros == []
        assert resultado.importados == 2

    def test_persiste_os_dados_corretamente(self, base_carregada: Session) -> None:
        _importar(
            base_carregada,
            [["Maria Silva", "Programação", "regular_seg_qua", "manha",
              "01/06/2026", "30/08/2026"]],
        )

        turma = base_carregada.scalar(select(TurmaEmAndamento))
        assert turma.instrutor.nome == "Maria Silva"
        assert turma.tipologia.nome == "Programação"
        assert turma.modalidade == Modalidade.REGULAR_SEG_QUA
        assert turma.turno == Turno.MANHA
        assert turma.data_inicio.isoformat() == "2026-06-01"
        assert turma.data_fim_prevista.isoformat() == "2026-08-30"

    def test_deriva_o_projeto_do_instrutor(self, base_carregada: Session) -> None:
        _importar(
            base_carregada,
            [["Maria Silva", "Programação", "regular_seg_qua", "manha",
              "01/06/2026", "30/08/2026"]],
        )

        turma = base_carregada.scalar(select(TurmaEmAndamento))
        assert turma.projeto.nome == "Jovem Digital"

    def test_planilha_vazia_e_cenario_valido(self, base_carregada: Session) -> None:
        """Sem turmas em curso, a simulação parte com todos os instrutores livres."""
        resultado = _importar(base_carregada, [])

        assert resultado.erro_arquivo is None
        assert resultado.erros == []
        assert resultado.importados == 0


class TestValidacao:
    def test_rejeita_instrutor_inexistente(self, base_carregada: Session) -> None:
        resultado = _importar(
            base_carregada,
            [["Fulano Inexistente", "Programação", "regular_seg_qua", "manha",
              "01/06/2026", "30/08/2026"]],
        )

        assert "não encontrado" in resultado.erros[0].motivo

    def test_rejeita_tipologia_inexistente(self, base_carregada: Session) -> None:
        resultado = _importar(
            base_carregada,
            [["Maria Silva", "Xadrez", "regular_seg_qua", "manha",
              "01/06/2026", "30/08/2026"]],
        )

        assert "não encontrada" in resultado.erros[0].motivo

    def test_rejeita_turno_incompativel_com_o_instrutor(self, base_carregada: Session) -> None:
        """Maria está disponível de manhã e à tarde, não à noite."""
        resultado = _importar(
            base_carregada,
            [["Maria Silva", "Programação", "regular_seg_qua", "noite",
              "01/06/2026", "30/08/2026"]],
        )

        assert "não está disponível no turno" in resultado.erros[0].motivo
        assert "manha, tarde" in resultado.erros[0].motivo

    def test_rejeita_modalidade_invalida(self, base_carregada: Session) -> None:
        resultado = _importar(
            base_carregada,
            [["Maria Silva", "Programação", "sexta_feira", "manha",
              "01/06/2026", "30/08/2026"]],
        )

        assert "Modalidade inválida" in resultado.erros[0].motivo

    def test_rejeita_termino_anterior_ao_inicio(self, base_carregada: Session) -> None:
        resultado = _importar(
            base_carregada,
            [["Maria Silva", "Programação", "regular_seg_qua", "manha",
              "30/08/2026", "01/06/2026"]],
        )

        assert "anterior" in resultado.erros[0].motivo

    def test_rejeita_data_em_formato_invalido(self, base_carregada: Session) -> None:
        resultado = _importar(
            base_carregada,
            [["Maria Silva", "Programação", "regular_seg_qua", "manha",
              "ontem", "30/08/2026"]],
        )

        assert "DD/MM/AAAA" in resultado.erros[0].motivo


class TestSobrecarga:
    def test_aceita_sobrecarga_com_alerta(self, base_carregada: Session) -> None:
        """É o retrato do mundo real, não erro de preenchimento.

        João tem 3h à noite; duas turmas de Robótica exigem 4h por encontro cada.
        """
        resultado = _importar(
            base_carregada,
            [
                ["João Souza", "Robótica", "regular_seg_qua", "noite",
                 "01/06/2026", "30/08/2026"],
                ["João Souza", "Robótica", "regular_ter_qui", "noite",
                 "01/06/2026", "30/08/2026"],
            ],
        )

        assert resultado.erros == []
        assert resultado.importados == 2
        assert any("acima da capacidade" in a.mensagem for a in resultado.alertas)

    def test_sem_alerta_quando_cabe_na_capacidade(self, base_carregada: Session) -> None:
        """Maria tem 4h de manhã; uma turma de Programação usa 3h por encontro."""
        resultado = _importar(
            base_carregada,
            [["Maria Silva", "Programação", "regular_seg_qua", "manha",
              "01/06/2026", "30/08/2026"]],
        )

        assert not any("acima da capacidade" in a.mensagem for a in resultado.alertas)

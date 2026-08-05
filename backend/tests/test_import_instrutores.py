"""Testes da importação da planilha de instrutores."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Instrutor, Projeto, Tipologia, Turno
from app.services.importacao.parser_instrutores import importar_instrutores
from tests.fabricas import csv_bytes, planilha_instrutores, xlsx_bytes


def _importar(db: Session, linhas: list[list[str]]):
    return importar_instrutores(db, planilha_instrutores(linhas), "instrutores.csv")


class TestImportacaoBemSucedida:
    def test_importa_multiplos_instrutores(self, db: Session) -> None:
        resultado = _importar(
            db,
            [
                ["Maria Silva", "Jovem Digital", "manha;tarde", "4;4", "2;3;4;5",
                 "Programação;Pixel Art"],
                ["João Souza", "Jovem Digital", "noite", "3", "2;4", "Robótica"],
                ["Ana Costa", "Inclusão Tech", "manha;noite", "4;3", "2;3;4;5;6",
                 "Robótica;Programação"],
            ],
        )

        assert resultado.erro_arquivo is None
        assert resultado.erros == []
        assert resultado.importados == 3

    def test_persiste_turnos_com_cargas_distintas(self, db: Session) -> None:
        _importar(db, [["Ana Costa", "Inclusão Tech", "manha;noite", "4;3", "2;4", "Robótica"]])

        instrutor = db.scalar(select(Instrutor).where(Instrutor.nome == "Ana Costa"))
        assert {t.turno: t.carga_horaria_horas for t in instrutor.turnos} == {
            Turno.MANHA: 4.0,
            Turno.NOITE: 3.0,
        }

    def test_persiste_dias_e_tipologias(self, db: Session) -> None:
        _importar(
            db,
            [["Maria Silva", "Jovem Digital", "manha", "4", "2;4", "Programação;Pixel Art"]],
        )

        instrutor = db.scalar(select(Instrutor).where(Instrutor.nome == "Maria Silva"))
        assert sorted(d.dia_semana for d in instrutor.dias) == [2, 4]
        assert sorted(v.tipologia.nome for v in instrutor.tipologias) == [
            "Pixel Art",
            "Programação",
        ]

    def test_aceita_formato_explicito_turno_horas(self, db: Session) -> None:
        conteudo = csv_bytes(
            ["nome", "projeto", "turnos", "dias_semana", "tipologias"],
            [["Maria Silva", "Jovem Digital", "manha:4;tarde:4", "2;4", "Programação"]],
        )

        resultado = importar_instrutores(db, conteudo, "instrutores.csv")

        assert resultado.erros == []
        instrutor = db.scalar(select(Instrutor).where(Instrutor.nome == "Maria Silva"))
        assert len(instrutor.turnos) == 2

    def test_aceita_xlsx(self, db: Session) -> None:
        conteudo = xlsx_bytes(
            ["nome", "projeto", "turnos", "carga_horaria_turno", "dias_semana", "tipologias"],
            [["Maria Silva", "Jovem Digital", "manha", 4, "2;4", "Programação"]],
        )

        resultado = importar_instrutores(db, conteudo, "instrutores.xlsx")

        assert resultado.erros == []
        assert resultado.importados == 1

    def test_aceita_cabecalhos_com_acento_maiuscula_e_ordem_trocada(self, db: Session) -> None:
        conteudo = csv_bytes(
            ["Tipologias", "NOME", "Dias Semana", "Projeto", "Turnos", "Carga Horária Turno"],
            [["Programação", "Maria Silva", "2;4", "Jovem Digital", "manha", "4"]],
        )

        resultado = importar_instrutores(db, conteudo, "instrutores.csv")

        assert resultado.erros == []
        assert db.scalar(select(Instrutor).where(Instrutor.nome == "Maria Silva")) is not None

    def test_remove_espacos_em_torno_dos_separadores(self, db: Session) -> None:
        _importar(
            db,
            [["Maria Silva", "Jovem Digital", "manha", "4", "2;4", "Programação ; Pixel Art"]],
        )

        nomes = sorted(t.nome for t in db.scalars(select(Tipologia)).all())
        assert nomes == ["Pixel Art", "Programação"]


class TestDerivacaoDeCatalogo:
    def test_cria_tipologias_ineditas_como_pendentes(self, db: Session) -> None:
        _importar(db, [["Maria Silva", "Jovem Digital", "manha", "4", "2;4", "Robótica"]])

        tipologia = db.scalar(select(Tipologia).where(Tipologia.nome == "Robótica"))
        assert tipologia is not None
        assert tipologia.configurada is False

    def test_cria_projetos_ineditos(self, db: Session) -> None:
        _importar(db, [["Maria Silva", "Projeto Novo", "manha", "4", "2;4", "Robótica"]])

        assert db.scalar(select(Projeto).where(Projeto.nome == "Projeto Novo")) is not None

    def test_reutiliza_tipologia_existente_sem_sobrescrever(self, db: Session) -> None:
        db.add(Tipologia(nome="Robótica", carga_horaria_total_horas=40, horas_por_encontro=4))
        db.commit()

        _importar(db, [["Maria Silva", "Jovem Digital", "manha", "4", "2;4", "Robótica"]])

        tipologias = db.scalars(select(Tipologia).where(Tipologia.nome == "Robótica")).all()
        assert len(tipologias) == 1
        assert tipologias[0].carga_horaria_total_horas == 40

    def test_alerta_sobre_tipologias_pendentes(self, db: Session) -> None:
        resultado = _importar(
            db, [["Maria Silva", "Jovem Digital", "manha", "4", "2;4", "Robótica;Pixel Art"]]
        )

        assert any("pendente" in a.mensagem for a in resultado.alertas)


class TestValidacaoPorLinha:
    def test_importa_validas_e_reporta_invalidas(self, db: Session) -> None:
        """Uma linha ruim não pode custar a planilha inteira."""
        resultado = _importar(
            db,
            [
                ["Maria Silva", "Jovem Digital", "manha", "4", "2;4", "Programação"],
                ["Erro Turnos", "Jovem Digital", "manha;tarde", "4", "2;4", "Programação"],
                ["João Souza", "Jovem Digital", "noite", "3", "2;4", "Robótica"],
            ],
        )

        assert resultado.importados == 2
        assert len(resultado.erros) == 1
        assert resultado.erros[0].linha == 3
        assert db.scalar(select(Instrutor).where(Instrutor.nome == "Erro Turnos")) is None
        assert db.scalar(select(Instrutor).where(Instrutor.nome == "João Souza")) is not None

    def test_rejeita_instrutor_sem_tipologia(self, db: Session) -> None:
        resultado = _importar(db, [["Maria Silva", "Jovem Digital", "manha", "4", "2;4", ""]])

        assert resultado.importados == 0
        assert "tipologia" in resultado.erros[0].motivo.lower()

    def test_rejeita_turno_invalido(self, db: Session) -> None:
        resultado = _importar(
            db, [["Maria Silva", "Jovem Digital", "madrugada", "4", "2;4", "Programação"]]
        )

        assert "Turno inválido" in resultado.erros[0].motivo

    def test_rejeita_dia_fora_da_faixa(self, db: Session) -> None:
        resultado = _importar(
            db, [["Maria Silva", "Jovem Digital", "manha", "4", "2;7", "Programação"]]
        )

        assert "fora da faixa" in resultado.erros[0].motivo

    def test_rejeita_desalinhamento_entre_turnos_e_cargas(self, db: Session) -> None:
        resultado = _importar(
            db, [["Maria Silva", "Jovem Digital", "manha;tarde", "4", "2;4", "Programação"]]
        )

        assert "mesma quantidade" in resultado.erros[0].motivo

    def test_rejeita_nome_vazio(self, db: Session) -> None:
        resultado = _importar(db, [["", "Jovem Digital", "manha", "4", "2;4", "Programação"]])

        assert "Nome" in resultado.erros[0].motivo

    def test_numero_da_linha_corresponde_a_planilha(self, db: Session) -> None:
        """A linha 2 é a primeira de dados, já que a 1 é o cabeçalho."""
        resultado = _importar(db, [["", "Jovem Digital", "manha", "4", "2;4", "Programação"]])

        assert resultado.erros[0].linha == 2

    def test_contador_nao_diverge_do_banco(self, db: Session) -> None:
        """O descarte de uma linha ruim não pode levar junto as anteriores.

        Sem SAVEPOINT por linha, o rollback desfazia a transação inteira e o
        contador continuava alto — perda silenciosa de dados.
        """
        resultado = _importar(
            db,
            [
                ["Maria Silva", "Jovem Digital", "manha", "4", "2;4", "Programação"],
                ["Erro Turnos", "Jovem Digital", "manha;tarde", "4", "2;4", "Programação"],
                ["João Souza", "Jovem Digital", "noite", "3", "2;4", "Robótica"],
                ["Erro Dia", "Jovem Digital", "manha", "4", "9", "Robótica"],
                ["Ana Costa", "Inclusão Tech", "tarde", "4", "3;5", "Pixel Art"],
            ],
        )

        no_banco = db.scalars(select(Instrutor)).all()
        assert resultado.importados == len(no_banco)
        assert sorted(i.nome for i in no_banco) == ["Ana Costa", "João Souza", "Maria Silva"]
        assert len(resultado.erros) == 2

    def test_nome_duplicado_na_mesma_planilha_e_reportado(self, db: Session) -> None:
        """A segunda ocorrência atualiza a primeira em vez de quebrar a importação."""
        resultado = _importar(
            db,
            [
                ["Maria Silva", "Jovem Digital", "manha", "4", "2;4", "Programação"],
                ["Maria Silva", "Jovem Digital", "noite", "3", "3;5", "Robótica"],
            ],
        )

        assert resultado.erro_arquivo is None
        instrutores = db.scalars(select(Instrutor).where(Instrutor.nome == "Maria Silva")).all()
        assert len(instrutores) == 1


class TestArquivoRecusado:
    def test_coluna_obrigatoria_ausente_recusa_o_arquivo(self, db: Session) -> None:
        conteudo = csv_bytes(
            ["nome", "projeto", "turnos", "carga_horaria_turno", "dias_semana"],
            [["Maria Silva", "Jovem Digital", "manha", "4", "2;4"]],
        )

        resultado = importar_instrutores(db, conteudo, "instrutores.csv")

        assert resultado.erro_arquivo is not None
        assert "tipologias" in resultado.erro_arquivo
        assert db.scalar(select(Instrutor)) is None

    def test_formato_nao_suportado_recusa_o_arquivo(self, db: Session) -> None:
        resultado = importar_instrutores(db, b"conteudo", "instrutores.pdf")

        assert resultado.erro_arquivo is not None
        assert ".xlsx" in resultado.erro_arquivo


class TestReimportacao:
    def test_atualiza_instrutor_existente_sem_duplicar(self, db: Session) -> None:
        _importar(db, [["Maria Silva", "Jovem Digital", "manha", "4", "2;4", "Programação"]])
        resultado = _importar(
            db,
            [["Maria Silva", "Jovem Digital", "manha;noite", "4;3", "2;3;4", "Robótica"]],
        )

        assert resultado.atualizados == 1
        assert resultado.importados == 0

        instrutores = db.scalars(select(Instrutor).where(Instrutor.nome == "Maria Silva")).all()
        assert len(instrutores) == 1

        instrutor = instrutores[0]
        assert len(instrutor.turnos) == 2
        assert sorted(d.dia_semana for d in instrutor.dias) == [2, 3, 4]
        assert [v.tipologia.nome for v in instrutor.tipologias] == ["Robótica"]

"""Testes da importação de datas não letivas (feriados, recessos, férias).

Persistidas na v1, mas sem efeito sobre o cálculo das simulações — a última
classe deste arquivo confirma exatamente essa ausência de efeito.
"""

from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import DataNaoLetiva, Projeto
from app.services.importacao.parser_datas_nao_letivas import importar_datas_nao_letivas
from tests.fabricas import planilha_datas_nao_letivas

CSV = "text/csv"


def _importar(db: Session, linhas: list[list[str]]):
    return importar_datas_nao_letivas(db, planilha_datas_nao_letivas(linhas), "datas.csv")


class TestImportacaoBemSucedida:
    def test_importa_dia_unico(self, db: Session) -> None:
        resultado = _importar(db, [["07/09/2026", "", "Independência", "feriado", ""]])

        assert resultado.erros == []
        assert resultado.importados == 1
        registro = db.query(DataNaoLetiva).one()
        assert registro.data_inicio == date(2026, 9, 7)
        assert registro.data_fim == date(2026, 9, 7)
        assert registro.tipo.value == "feriado"
        assert registro.projeto_id is None

    def test_importa_intervalo(self, db: Session) -> None:
        resultado = _importar(
            db,
            [["24/12/2026", "06/01/2027", "Recesso de fim de ano", "recesso", ""]],
        )

        assert resultado.erros == []
        registro = db.query(DataNaoLetiva).one()
        assert registro.data_inicio == date(2026, 12, 24)
        assert registro.data_fim == date(2027, 1, 6)
        assert registro.tipo.value == "recesso"

    def test_tipo_padrao_e_feriado_quando_ausente(self, db: Session) -> None:
        _importar(db, [["07/09/2026", "", "Independência", "", ""]])

        registro = db.query(DataNaoLetiva).one()
        assert registro.tipo.value == "feriado"

    def test_resolve_projeto_por_nome(self, db: Session) -> None:
        db.add(Projeto(nome="Inclusão Tech"))
        db.commit()

        _importar(
            db,
            [["15/03/2027", "19/03/2027", "Férias da equipe", "ferias", "Inclusão Tech"]],
        )

        registro = db.query(DataNaoLetiva).one()
        assert registro.projeto.nome == "Inclusão Tech"

    def test_projeto_vazio_aplica_a_todos(self, db: Session) -> None:
        _importar(db, [["07/09/2026", "", "Independência", "feriado", ""]])

        registro = db.query(DataNaoLetiva).one()
        assert registro.projeto_id is None

    def test_intervalos_sobrepostos_nao_sao_consolidados(self, db: Session) -> None:
        resultado = _importar(
            db,
            [
                ["24/12/2026", "31/12/2026", "Recesso parte 1", "recesso", ""],
                ["28/12/2026", "06/01/2027", "Recesso parte 2", "recesso", ""],
            ],
        )

        assert resultado.erros == []
        assert resultado.importados == 2
        assert db.query(DataNaoLetiva).count() == 2


class TestValidacao:
    def test_rejeita_termino_anterior_ao_inicio(self, db: Session) -> None:
        resultado = _importar(
            db, [["06/01/2027", "24/12/2026", "Recesso invertido", "recesso", ""]]
        )

        assert "anterior" in resultado.erros[0].motivo
        assert db.query(DataNaoLetiva).count() == 0

    def test_rejeita_projeto_inexistente(self, db: Session) -> None:
        resultado = _importar(
            db,
            [["07/09/2026", "", "Independência", "feriado", "Projeto Fantasma"]],
        )

        assert "não encontrado" in resultado.erros[0].motivo

    def test_aceita_projeto_vazio(self, db: Session) -> None:
        resultado = _importar(db, [["07/09/2026", "", "Independência", "feriado", ""]])

        assert resultado.erros == []

    def test_rejeita_data_em_formato_invalido(self, db: Session) -> None:
        resultado = _importar(db, [["ontem", "", "Feriado qualquer", "feriado", ""]])

        assert "DD/MM/AAAA" in resultado.erros[0].motivo

    def test_rejeita_tipo_invalido(self, db: Session) -> None:
        resultado = _importar(db, [["07/09/2026", "", "Independência", "carnaval", ""]])

        assert "Tipo inválido" in resultado.erros[0].motivo


class TestAlertaSemEfeitoPratico:
    def test_alerta_para_fim_de_semana(self, db: Session) -> None:
        # 05/09/2026 é sábado.
        resultado = _importar(db, [["05/09/2026", "06/09/2026", "Fim de semana", "feriado", ""]])

        assert any("sem efeito prático" in a.mensagem for a in resultado.alertas)

    def test_alerta_para_sexta_feira(self, db: Session) -> None:
        # 04/09/2026 é sexta-feira.
        resultado = _importar(db, [["04/09/2026", "", "Só sexta", "feriado", ""]])

        assert any("sem efeito prático" in a.mensagem for a in resultado.alertas)

    def test_sem_alerta_para_dia_util(self, db: Session) -> None:
        # 07/09/2026 é segunda-feira.
        resultado = _importar(db, [["07/09/2026", "", "Independência", "feriado", ""]])

        assert not any("sem efeito prático" in a.mensagem for a in resultado.alertas)

    def test_aviso_geral_de_ausencia_de_efeito_sempre_presente(self, db: Session) -> None:
        resultado = _importar(db, [["07/09/2026", "", "Independência", "feriado", ""]])

        assert any("ainda não afetam o cálculo" in a.mensagem for a in resultado.alertas)


class TestApiConsulta:
    def test_lista_com_aviso_de_ausencia_de_efeito(self, client: TestClient) -> None:
        client.post(
            "/datas-nao-letivas",
            json={
                "data_inicio": "2026-09-07",
                "descricao": "Independência",
                "tipo": "feriado",
            },
        )

        resposta = client.get("/datas-nao-letivas")

        assert resposta.status_code == 200
        corpo = resposta.json()
        assert len(corpo["itens"]) == 1
        assert "ainda não afetam o cálculo" in corpo["aviso"]

    def test_filtra_por_periodo_intersecao(self, client: TestClient) -> None:
        client.post(
            "/datas-nao-letivas",
            json={
                "data_inicio": "2026-12-24",
                "data_fim": "2027-01-06",
                "descricao": "Recesso de fim de ano",
                "tipo": "recesso",
            },
        )
        client.post(
            "/datas-nao-letivas",
            json={
                "data_inicio": "2026-09-07",
                "descricao": "Independência",
                "tipo": "feriado",
            },
        )

        # Janela que só intersecciona o recesso, não o feriado de setembro.
        resposta = client.get("/datas-nao-letivas?de=2026-12-01&ate=2027-01-31")

        corpo = resposta.json()
        assert len(corpo["itens"]) == 1
        assert corpo["itens"][0]["descricao"] == "Recesso de fim de ano"

    def test_filtra_por_projeto(self, client: TestClient) -> None:
        projeto = client.post("/projetos", json={"nome": "Inclusão Tech"}).json()
        client.post(
            "/datas-nao-letivas",
            json={
                "data_inicio": "2027-03-15",
                "data_fim": "2027-03-19",
                "descricao": "Férias da equipe",
                "tipo": "ferias",
                "projeto_id": projeto["id"],
            },
        )
        client.post(
            "/datas-nao-letivas",
            json={
                "data_inicio": "2026-09-07",
                "descricao": "Independência",
                "tipo": "feriado",
            },
        )

        resposta = client.get(f"/datas-nao-letivas?projeto_id={projeto['id']}")

        corpo = resposta.json()
        assert len(corpo["itens"]) == 1
        assert corpo["itens"][0]["descricao"] == "Férias da equipe"

    def test_cria_atualiza_e_remove(self, client: TestClient) -> None:
        criado = client.post(
            "/datas-nao-letivas",
            json={
                "data_inicio": "2026-09-07",
                "descricao": "Independência",
                "tipo": "feriado",
            },
        ).json()

        atualizado = client.put(
            f"/datas-nao-letivas/{criado['id']}",
            json={
                "data_inicio": "2026-09-07",
                "descricao": "Independência do Brasil",
                "tipo": "feriado",
            },
        ).json()
        assert atualizado["descricao"] == "Independência do Brasil"

        remocao = client.delete(f"/datas-nao-letivas/{criado['id']}")
        assert remocao.status_code == 204
        assert client.get("/datas-nao-letivas").json()["itens"] == []

    def test_rejeita_termino_anterior_ao_inicio(self, client: TestClient) -> None:
        resposta = client.post(
            "/datas-nao-letivas",
            json={
                "data_inicio": "2027-01-06",
                "data_fim": "2026-12-24",
                "descricao": "Recesso invertido",
                "tipo": "recesso",
            },
        )
        assert resposta.status_code == 422

    def test_importar_via_api_expoe_aviso_nos_alertas(self, client: TestClient) -> None:
        resposta = client.post(
            "/importar/datas-nao-letivas",
            files={
                "arquivo": (
                    "datas.csv",
                    planilha_datas_nao_letivas(
                        [["07/09/2026", "", "Independência", "feriado", ""]]
                    ),
                    CSV,
                )
            },
        )

        assert resposta.status_code == 200
        corpo = resposta.json()
        assert corpo["importados"] == 1
        assert any("ainda não afetam o cálculo" in a["mensagem"] for a in corpo["alertas"])


@pytest.fixture
def base_com_instrutor(client: TestClient) -> TestClient:
    """Um instrutor multi-tipologia, sem turmas em andamento, pronto para simular."""
    from tests.fabricas import planilha_instrutores, planilha_tipologias

    resposta = client.post(
        "/importar/instrutores",
        files={
            "arquivo": (
                "instrutores.csv",
                planilha_instrutores(
                    [
                        [
                            "Maria Silva",
                            "Jovem Digital",
                            "manha_1",
                            "2;3;4;5",
                            "Programação;Pixel Art",
                        ]
                    ]
                ),
                CSV,
            )
        },
    )
    assert resposta.status_code == 200
    resposta = client.post(
        "/importar/tipologias",
        files={
            "arquivo": (
                "tipologias.csv",
                planilha_tipologias([["Programação", "60", "3"], ["Pixel Art", "24", "2"]]),
                CSV,
            )
        },
    )
    assert resposta.status_code == 200
    return client


def _executar_e_obter_resultado(client: TestClient) -> dict:
    cenario = client.post(
        "/cenarios",
        json={
            "nome": "Cenário de teste",
            "periodo_de": "2026-08-31",
            "periodo_ate": "2026-11-30",
            "pesos_objetivo": {
                "maximizar_aproveitamento": 1.0,
                "antecipar_inicio": 0.0,
                "balancear_carga_instrutores": 0.0,
                "balancear_tipologias": 0.0,
            },
        },
    ).json()
    disparo = client.post("/simulacoes/executar", json={"cenario_id": cenario["id"]}).json()

    turmas = client.get(f"/simulacoes/{disparo['id']}/turmas-sugeridas").json()
    kpis = client.get(f"/simulacoes/{disparo['id']}/kpis").json()
    for turma in turmas:
        del turma["id"]
    return {"turmas": turmas, "kpis": kpis}


class TestAusenciaDeEfeitoNaSimulacao:
    def test_feriados_cadastrados_nao_alteram_o_resultado(
        self, base_com_instrutor: TestClient
    ) -> None:
        """Confirma o design da v1: o gerador de calendário ainda não consulta
        `datas_nao_letivas`, então uma base com feriados cadastrados produz
        exatamente o mesmo resultado que uma base sem eles."""
        resultado_sem_feriados = _executar_e_obter_resultado(base_com_instrutor)

        base_com_instrutor.post(
            "/datas-nao-letivas",
            json={
                "data_inicio": "2026-09-07",
                "descricao": "Independência",
                "tipo": "feriado",
            },
        )
        base_com_instrutor.post(
            "/datas-nao-letivas",
            json={
                "data_inicio": "2026-10-12",
                "descricao": "Nossa Senhora Aparecida",
                "tipo": "feriado",
            },
        )

        resultado_com_feriados = _executar_e_obter_resultado(base_com_instrutor)

        assert resultado_com_feriados == resultado_sem_feriados

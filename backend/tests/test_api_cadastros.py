"""Testes dos CRUDs de cadastro."""

import pytest
from fastapi.testclient import TestClient

from tests.fabricas import planilha_instrutores, planilha_tipologias

CSV = "text/csv"


@pytest.fixture
def base(client: TestClient) -> TestClient:
    """Base carregada por importação, como no uso real."""
    client.post(
        "/importar/instrutores",
        files={
            "arquivo": (
                "i.csv",
                planilha_instrutores(
                    [
                        ["Maria Silva", "Jovem Digital", "manha;tarde", "4;4", "2;3;4;5",
                         "Programação;Pixel Art"],
                        ["João Souza", "Inclusão Tech", "noite", "3", "2;4", "Robótica"],
                    ]
                ),
                CSV,
            )
        },
    )
    client.post(
        "/importar/tipologias",
        files={
            "arquivo": (
                "t.csv",
                planilha_tipologias(
                    [["Programação", "60", "3"], ["Pixel Art", "24", "2"], ["Robótica", "40", "4"]]
                ),
                CSV,
            )
        },
    )
    return client


class TestProjetos:
    def test_lista_com_contagem_de_instrutores(self, base: TestClient) -> None:
        projetos = base.get("/projetos").json()

        por_nome = {p["nome"]: p for p in projetos}
        assert por_nome["Jovem Digital"]["total_instrutores"] == 1
        assert por_nome["Inclusão Tech"]["total_instrutores"] == 1

    def test_cria_projeto(self, client: TestClient) -> None:
        resposta = client.post("/projetos", json={"nome": "Projeto Novo"})

        assert resposta.status_code == 201
        assert resposta.json()["nome"] == "Projeto Novo"

    def test_recusa_nome_duplicado(self, base: TestClient) -> None:
        resposta = base.post("/projetos", json={"nome": "Jovem Digital"})

        assert resposta.status_code == 409

    def test_recusa_remover_projeto_com_instrutores(self, base: TestClient) -> None:
        projeto_id = next(p["id"] for p in base.get("/projetos").json()
                          if p["nome"] == "Jovem Digital")

        resposta = base.delete(f"/projetos/{projeto_id}")

        assert resposta.status_code == 409
        assert "instrutor" in resposta.json()["detail"]


class TestTipologias:
    def test_lista_com_dados_derivados(self, base: TestClient) -> None:
        tipologias = {t["nome"]: t for t in base.get("/tipologias").json()}

        robotica = tipologias["Robótica"]
        assert robotica["configurada"] is True
        assert robotica["num_encontros"] == 10
        assert robotica["total_instrutores"] == 1

    def test_pendentes_vazio_apos_configurar(self, base: TestClient) -> None:
        assert base.get("/tipologias/pendentes").json() == []

    def test_lista_pendente_apos_importar_instrutor_com_tipologia_nova(
        self, base: TestClient
    ) -> None:
        base.post(
            "/importar/instrutores",
            files={
                "arquivo": (
                    "i.csv",
                    planilha_instrutores(
                        [["Ana Costa", "Jovem Digital", "manha", "4", "2;4", "Xadrez"]]
                    ),
                    CSV,
                )
            },
        )

        pendentes = base.get("/tipologias/pendentes").json()

        assert [p["nome"] for p in pendentes] == ["Xadrez"]

    def test_recusa_carga_nao_divisivel(self, client: TestClient) -> None:
        resposta = client.post(
            "/tipologias",
            json={"nome": "Teste", "carga_horaria_total_horas": 50, "horas_por_encontro": 4},
        )

        assert resposta.status_code == 422
        assert "múltiplo exato" in str(resposta.json())

    def test_recusa_carga_fora_da_faixa(self, client: TestClient) -> None:
        resposta = client.post(
            "/tipologias",
            json={"nome": "Teste", "carga_horaria_total_horas": 80, "horas_por_encontro": 4},
        )

        assert resposta.status_code == 422

    def test_aceita_carga_divisivel(self, client: TestClient) -> None:
        resposta = client.post(
            "/tipologias",
            json={"nome": "Teste", "carga_horaria_total_horas": 40, "horas_por_encontro": 4},
        )

        assert resposta.status_code == 201
        assert resposta.json()["num_encontros"] == 10


class TestInstrutores:
    def test_lista_com_turnos_dias_e_tipologias(self, base: TestClient) -> None:
        instrutores = {i["nome"]: i for i in base.get("/instrutores").json()}

        maria = instrutores["Maria Silva"]
        assert maria["projeto_nome"] == "Jovem Digital"
        assert {t["turno"]: t["carga_horaria_horas"] for t in maria["turnos"]} == {
            "manha": 4.0,
            "tarde": 4.0,
        }
        assert maria["dias_semana"] == [2, 3, 4, 5]
        assert maria["tipologias"] == ["Pixel Art", "Programação"]

    def test_filtra_por_projeto(self, base: TestClient) -> None:
        projeto_id = next(p["id"] for p in base.get("/projetos").json()
                          if p["nome"] == "Inclusão Tech")

        instrutores = base.get(f"/instrutores?projeto_id={projeto_id}").json()

        assert [i["nome"] for i in instrutores] == ["João Souza"]

    def test_filtra_por_tipologia(self, base: TestClient) -> None:
        tipologia_id = next(t["id"] for t in base.get("/tipologias").json()
                            if t["nome"] == "Robótica")

        instrutores = base.get(f"/instrutores?tipologia_id={tipologia_id}").json()

        assert [i["nome"] for i in instrutores] == ["João Souza"]

    def test_edita_disponibilidade(self, base: TestClient) -> None:
        maria = next(i for i in base.get("/instrutores").json() if i["nome"] == "Maria Silva")
        tipologia_id = next(t["id"] for t in base.get("/tipologias").json()
                            if t["nome"] == "Programação")

        resposta = base.put(
            f"/instrutores/{maria['id']}",
            json={
                "nome": "Maria Silva",
                "projeto_id": maria["projeto_id"],
                "turnos": [{"turno": "noite", "carga_horaria_horas": 3}],
                "dias_semana": [3, 5],
                "tipologia_ids": [tipologia_id],
            },
        )

        assert resposta.status_code == 200
        corpo = resposta.json()
        assert [t["turno"] for t in corpo["turnos"]] == ["noite"]
        assert corpo["dias_semana"] == [3, 5]
        assert corpo["tipologias"] == ["Programação"]

    def test_recusa_dia_fora_da_faixa(self, base: TestClient) -> None:
        maria = next(i for i in base.get("/instrutores").json() if i["nome"] == "Maria Silva")
        tipologia_id = next(t["id"] for t in base.get("/tipologias").json())

        resposta = base.put(
            f"/instrutores/{maria['id']}",
            json={
                "nome": "Maria Silva",
                "projeto_id": maria["projeto_id"],
                "turnos": [{"turno": "manha", "carga_horaria_horas": 4}],
                "dias_semana": [7],
                "tipologia_ids": [tipologia_id],
            },
        )

        assert resposta.status_code == 422

    def test_instrutor_inexistente_retorna_404(self, base: TestClient) -> None:
        assert base.get("/instrutores/9999").status_code == 404


class TestTurmasEmAndamento:
    def _dados_turma(self, base: TestClient, turno: str = "manha") -> dict:
        maria = next(i for i in base.get("/instrutores").json() if i["nome"] == "Maria Silva")
        tipologia_id = next(t["id"] for t in base.get("/tipologias").json()
                            if t["nome"] == "Programação")
        return {
            "instrutor_id": maria["id"],
            "tipologia_id": tipologia_id,
            "modalidade": "regular_seg_qua",
            "turno": turno,
            "data_inicio": "2026-06-01",
            "data_fim_prevista": "2026-08-30",
        }

    def test_cria_turma(self, base: TestClient) -> None:
        resposta = base.post("/turmas-em-andamento", json=self._dados_turma(base))

        assert resposta.status_code == 201
        corpo = resposta.json()
        assert corpo["instrutor_nome"] == "Maria Silva"
        assert corpo["tipologia_nome"] == "Programação"

    def test_recusa_turno_incompativel(self, base: TestClient) -> None:
        """Maria está disponível de manhã e à tarde, não à noite."""
        resposta = base.post("/turmas-em-andamento", json=self._dados_turma(base, turno="noite"))

        assert resposta.status_code == 422
        assert "não está disponível no turno" in resposta.json()["detail"]

    def test_recusa_datas_invertidas(self, base: TestClient) -> None:
        dados = self._dados_turma(base)
        dados["data_fim_prevista"] = "2026-01-01"

        resposta = base.post("/turmas-em-andamento", json=dados)

        assert resposta.status_code == 422

    def test_lista_ordenada_por_termino(self, base: TestClient) -> None:
        primeira = self._dados_turma(base)
        primeira["data_fim_prevista"] = "2026-10-30"
        base.post("/turmas-em-andamento", json=primeira)

        segunda = self._dados_turma(base, turno="tarde")
        segunda["data_fim_prevista"] = "2026-08-30"
        base.post("/turmas-em-andamento", json=segunda)

        turmas = base.get("/turmas-em-andamento").json()

        assert [t["data_fim_prevista"] for t in turmas] == ["2026-08-30", "2026-10-30"]

    def test_remove_turma(self, base: TestClient) -> None:
        turma_id = base.post("/turmas-em-andamento", json=self._dados_turma(base)).json()["id"]

        assert base.delete(f"/turmas-em-andamento/{turma_id}").status_code == 204
        assert base.get("/turmas-em-andamento").json() == []

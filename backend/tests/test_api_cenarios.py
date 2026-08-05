"""Testes do CRUD de cenários de simulação."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import Projeto

DADOS_BASICOS = {
    "nome": "Cenário base",
    "periodo_de": "2026-08-31",
    "periodo_ate": "2027-04-30",
    "pesos_objetivo": {
        "maximizar_aproveitamento": 0.4,
        "antecipar_inicio": 0.2,
        "balancear_carga_instrutores": 0.2,
        "balancear_tipologias": 0.2,
    },
}


@pytest.fixture
def projeto(db: Session) -> Projeto:
    p = Projeto(nome="Jovem Digital")
    db.add(p)
    db.commit()
    return p


class TestCriacao:
    def test_cria_cenario_com_json_correspondente(self, client: TestClient) -> None:
        resposta = client.post("/cenarios", json=DADOS_BASICOS)

        assert resposta.status_code == 201
        corpo = resposta.json()
        assert corpo["nome"] == "Cenário base"
        assert corpo["pesos_objetivo"]["maximizar_aproveitamento"] == 0.4
        assert corpo["projeto_ids"] == []

    def test_cria_com_escopo_de_projetos(self, client: TestClient, projeto: Projeto) -> None:
        dados = {**DADOS_BASICOS, "projeto_ids": [projeto.id]}
        resposta = client.post("/cenarios", json=dados)

        assert resposta.status_code == 201
        assert resposta.json()["projeto_ids"] == [projeto.id]

    def test_recusa_projeto_inexistente(self, client: TestClient) -> None:
        dados = {**DADOS_BASICOS, "projeto_ids": [9999]}
        resposta = client.post("/cenarios", json=dados)

        assert resposta.status_code == 404

    def test_recusa_periodo_invertido(self, client: TestClient) -> None:
        dados = {**DADOS_BASICOS, "periodo_de": "2027-01-01", "periodo_ate": "2026-01-01"}
        resposta = client.post("/cenarios", json=dados)

        assert resposta.status_code == 422

    def test_recusa_pesos_negativos(self, client: TestClient) -> None:
        dados = {
            **DADOS_BASICOS,
            "pesos_objetivo": {
                "maximizar_aproveitamento": -0.1,
                "antecipar_inicio": 0.2,
                "balancear_carga_instrutores": 0.2,
                "balancear_tipologias": 0.2,
            },
        }
        resposta = client.post("/cenarios", json=dados)

        assert resposta.status_code == 422

    def test_recusa_todos_os_pesos_nulos(self, client: TestClient) -> None:
        dados = {
            **DADOS_BASICOS,
            "pesos_objetivo": {
                "maximizar_aproveitamento": 0.0,
                "antecipar_inicio": 0.0,
                "balancear_carga_instrutores": 0.0,
                "balancear_tipologias": 0.0,
            },
        }
        resposta = client.post("/cenarios", json=dados)

        assert resposta.status_code == 422


class TestConsulta:
    def test_lista_cenarios(self, client: TestClient) -> None:
        client.post("/cenarios", json=DADOS_BASICOS)
        client.post("/cenarios", json={**DADOS_BASICOS, "nome": "Outro cenário"})

        resposta = client.get("/cenarios")

        assert resposta.status_code == 200
        assert len(resposta.json()) == 2

    def test_cenario_inexistente_retorna_404(self, client: TestClient) -> None:
        assert client.get("/cenarios/9999").status_code == 404


class TestAtualizacao:
    def test_atualiza_os_pesos(self, client: TestClient) -> None:
        criado = client.post("/cenarios", json=DADOS_BASICOS).json()

        dados_atualizados = {
            **DADOS_BASICOS,
            "pesos_objetivo": {
                "maximizar_aproveitamento": 1.0,
                "antecipar_inicio": 0.0,
                "balancear_carga_instrutores": 0.0,
                "balancear_tipologias": 0.0,
            },
        }
        resposta = client.put(f"/cenarios/{criado['id']}", json=dados_atualizados)

        assert resposta.status_code == 200
        assert resposta.json()["pesos_objetivo"]["maximizar_aproveitamento"] == 1.0

    def test_atualizar_cenario_inexistente_retorna_404(self, client: TestClient) -> None:
        resposta = client.put("/cenarios/9999", json=DADOS_BASICOS)
        assert resposta.status_code == 404


class TestDuplicacao:
    def test_duplica_com_os_mesmos_parametros(self, client: TestClient) -> None:
        original = client.post("/cenarios", json=DADOS_BASICOS).json()

        resposta = client.post(f"/cenarios/{original['id']}/duplicar")

        assert resposta.status_code == 201
        copia = resposta.json()
        assert copia["id"] != original["id"]
        assert "cópia" in copia["nome"]
        assert copia["pesos_objetivo"] == original["pesos_objetivo"]

    def test_editar_a_copia_nao_afeta_o_original(self, client: TestClient) -> None:
        original = client.post("/cenarios", json=DADOS_BASICOS).json()
        copia = client.post(f"/cenarios/{original['id']}/duplicar").json()

        dados_editados = {
            **DADOS_BASICOS,
            "nome": copia["nome"],
            "pesos_objetivo": {
                "maximizar_aproveitamento": 1.0,
                "antecipar_inicio": 0.0,
                "balancear_carga_instrutores": 0.0,
                "balancear_tipologias": 0.0,
            },
        }
        client.put(f"/cenarios/{copia['id']}", json=dados_editados)

        original_relido = client.get(f"/cenarios/{original['id']}").json()
        assert original_relido["pesos_objetivo"]["maximizar_aproveitamento"] == 0.4


class TestRemocao:
    def test_remove_cenario(self, client: TestClient) -> None:
        criado = client.post("/cenarios", json=DADOS_BASICOS).json()

        assert client.delete(f"/cenarios/{criado['id']}").status_code == 204
        assert client.get(f"/cenarios/{criado['id']}").status_code == 404

    def test_remover_cenario_inexistente_retorna_404(self, client: TestClient) -> None:
        assert client.delete("/cenarios/9999").status_code == 404

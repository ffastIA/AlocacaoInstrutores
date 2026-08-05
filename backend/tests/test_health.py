"""Testes da aplicação FastAPI e do endpoint de saúde."""

from fastapi.testclient import TestClient


def test_health_retorna_200_e_banco_conectado(client: TestClient) -> None:
    resposta = client.get("/health")

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["status"] == "ok"
    assert corpo["banco"]["conectado"] is True
    assert corpo["banco"]["erro"] is None


def test_health_informa_aplicacao_e_versao(client: TestClient) -> None:
    corpo = client.get("/health").json()

    assert corpo["aplicacao"]
    assert corpo["versao"]


def test_docs_disponivel(client: TestClient) -> None:
    assert client.get("/docs").status_code == 200


def test_openapi_expoe_endpoints(client: TestClient) -> None:
    esquema = client.get("/openapi.json").json()

    assert "/health" in esquema["paths"]


def test_acesso_sem_autenticacao(client: TestClient) -> None:
    """O sistema é aberto: nenhuma rota deve exigir credenciais."""
    for rota in ("/", "/health", "/docs"):
        resposta = client.get(rota)
        assert resposta.status_code not in (401, 403), rota

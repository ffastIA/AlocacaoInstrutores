"""Testes da persistência de parâmetros de cenário em JSON."""

import pytest
from pydantic import ValidationError

from app.services.cenarios.parametros import (
    ArquivoParametrosError,
    EscopoJson,
    ParametrosCenario,
    PeriodoJson,
    PesosObjetivoJson,
    atualizar_parametros,
    carregar_parametros,
    remover_parametros,
    salvar_parametros,
)


def _parametros(**overrides) -> ParametrosCenario:
    base = {
        "cenario_id": "1",
        "periodo": PeriodoJson(de="2026-08-31", ate="2027-04-30"),
        "pesos_objetivo": PesosObjetivoJson(
            maximizar_aproveitamento=0.4,
            antecipar_inicio=0.2,
            balancear_carga_instrutores=0.2,
            balancear_tipologias=0.2,
        ),
    }
    base.update(overrides)
    return ParametrosCenario(**base)


class TestSalvarECarregar:
    def test_ciclo_completo(self) -> None:
        parametros = _parametros()
        nome_arquivo = salvar_parametros(parametros)

        carregado = carregar_parametros(nome_arquivo)

        assert carregado.cenario_id == "1"
        assert carregado.pesos_objetivo.maximizar_aproveitamento == 0.4

        remover_parametros(nome_arquivo)

    def test_cada_cenario_gera_arquivo_proprio(self) -> None:
        nome1 = salvar_parametros(_parametros(cenario_id="1"))
        nome2 = salvar_parametros(_parametros(cenario_id="2"))

        assert nome1 != nome2


class TestAtualizacao:
    def test_atualizar_gera_um_novo_arquivo(self) -> None:
        """Editar nunca sobrescreve em disco — simulações passadas guardam seu
        próprio caminho e não podem ser afetadas retroativamente."""
        original = salvar_parametros(_parametros())

        atualizado = _parametros(
            pesos_objetivo=PesosObjetivoJson(
                maximizar_aproveitamento=1.0,
                antecipar_inicio=0.0,
                balancear_carga_instrutores=0.0,
                balancear_tipologias=0.0,
            )
        )
        novo_arquivo = atualizar_parametros(atualizado)

        assert novo_arquivo != original
        # O arquivo antigo continua intacto com os pesos originais.
        antigo_recarregado = carregar_parametros(original)
        assert antigo_recarregado.pesos_objetivo.maximizar_aproveitamento == 0.4

        novo_recarregado = carregar_parametros(novo_arquivo)
        assert novo_recarregado.pesos_objetivo.maximizar_aproveitamento == 1.0


class TestFalhaExplicita:
    def test_arquivo_ausente_nunca_usa_padrao(self) -> None:
        """Rodar com pesos diferentes dos configurados seria o pior tipo de erro."""
        with pytest.raises(ArquivoParametrosError, match="não encontrado"):
            carregar_parametros("inexistente.json")

    def test_arquivo_corrompido_falha(self, tmp_path) -> None:
        from app.core.config import settings

        caminho = settings.caminho_cenarios
        caminho.mkdir(parents=True, exist_ok=True)
        (caminho / "corrompido.json").write_text("{ nao é json valido", encoding="utf-8")

        with pytest.raises(ArquivoParametrosError, match="corrompido"):
            carregar_parametros("corrompido.json")

    def test_versao_de_schema_desconhecida_falha(self, tmp_path) -> None:
        from app.core.config import settings

        caminho = settings.caminho_cenarios
        caminho.mkdir(parents=True, exist_ok=True)
        (caminho / "versao_futura.json").write_text(
            '{"cenario_id": "1", "versao_schema": "99.0", '
            '"periodo": {"de": "2026-01-01", "ate": "2026-02-01"}, '
            '"pesos_objetivo": {"maximizar_aproveitamento": 1, "antecipar_inicio": 0, '
            '"balancear_carga_instrutores": 0, "balancear_tipologias": 0}}',
            encoding="utf-8",
        )

        with pytest.raises(ArquivoParametrosError):
            carregar_parametros("versao_futura.json")


class TestValidacao:
    def test_periodo_invertido_e_rejeitado(self) -> None:
        with pytest.raises(ValidationError, match="anterior"):
            PeriodoJson(de="2027-01-01", ate="2026-01-01")

    def test_peso_negativo_e_rejeitado(self) -> None:
        with pytest.raises(ValidationError):
            PesosObjetivoJson(
                maximizar_aproveitamento=-0.1,
                antecipar_inicio=0.2,
                balancear_carga_instrutores=0.2,
                balancear_tipologias=0.2,
            )

    def test_todos_os_pesos_zerados_e_rejeitado(self) -> None:
        with pytest.raises(ValidationError, match="zerados"):
            PesosObjetivoJson(
                maximizar_aproveitamento=0.0,
                antecipar_inicio=0.0,
                balancear_carga_instrutores=0.0,
                balancear_tipologias=0.0,
            )

    def test_escopo_vazio_e_valido_significa_todos_os_projetos(self) -> None:
        escopo = EscopoJson()
        assert escopo.projetos == []

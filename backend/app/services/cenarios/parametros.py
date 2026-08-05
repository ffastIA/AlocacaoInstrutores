"""Parâmetros de cenário persistidos em JSON.

Os pesos e a configuração do solver ficam em arquivo, não no banco: são
configuração comparável entre cenários, legível e editável fora do sistema. A
tabela `cenarios` guarda apenas o caminho do arquivo (ver
`app.models.models.Cenario`).

Falhar explicitamente quando o arquivo está ausente ou corrompido é
deliberado: uma simulação rodada com pesos diferentes dos que o usuário
configurou produziria um resultado plausível e errado — o pior tipo de falha
numa ferramenta de apoio à decisão.
"""

import json
import uuid
from datetime import date
from pathlib import Path

from pydantic import BaseModel, Field, field_validator, model_validator

from app.core.config import settings

VERSAO_SCHEMA_ATUAL = "1.0"


class PesosObjetivoJson(BaseModel):
    maximizar_aproveitamento: float = Field(ge=0)
    antecipar_inicio: float = Field(ge=0)
    balancear_carga_instrutores: float = Field(ge=0)
    balancear_tipologias: float = Field(ge=0)

    @model_validator(mode="after")
    def _exige_algum_peso_positivo(self) -> "PesosObjetivoJson":
        if not any(
            v > 0
            for v in (
                self.maximizar_aproveitamento,
                self.antecipar_inicio,
                self.balancear_carga_instrutores,
                self.balancear_tipologias,
            )
        ):
            raise ValueError(
                "Todos os pesos estão zerados — não haveria critério de otimização"
            )
        return self


class NormalizacaoJson(BaseModel):
    metodo: str = "estimado_por_cenario"
    fatores: dict[str, float] = Field(default_factory=dict)


class EscopoJson(BaseModel):
    projetos: list[str] = Field(default_factory=list)
    permitir_compartilhamento_entre_projetos: bool = False


class PeriodoJson(BaseModel):
    de: date
    ate: date

    @model_validator(mode="after")
    def _valida_intervalo(self) -> "PeriodoJson":
        if self.ate < self.de:
            raise ValueError("Data final do período é anterior à data inicial")
        return self


class RestricoesJson(BaseModel):
    max_turmas_por_dia: int = 4
    sexta_apenas_reposicao: bool = True
    modalidades_permitidas: list[str] = Field(
        default_factory=lambda: ["regular_seg_qua", "regular_ter_qui", "intensiva_seg_qui"]
    )


class SolverConfigJson(BaseModel):
    time_limit_seg: int = 180
    num_workers: int = 8
    gap_relativo: float = 0.02
    seed: int = 42


class ParametrosCenario(BaseModel):
    """Estrutura completa do arquivo JSON de um cenário."""

    cenario_id: str
    versao_schema: str = VERSAO_SCHEMA_ATUAL
    descricao: str | None = None
    periodo: PeriodoJson
    escopo: EscopoJson = Field(default_factory=EscopoJson)
    pesos_objetivo: PesosObjetivoJson
    normalizacao: NormalizacaoJson = Field(default_factory=NormalizacaoJson)
    restricoes: RestricoesJson = Field(default_factory=RestricoesJson)
    solver: SolverConfigJson = Field(default_factory=SolverConfigJson)

    @field_validator("versao_schema")
    @classmethod
    def _valida_versao_conhecida(cls, v: str) -> str:
        if v != VERSAO_SCHEMA_ATUAL:
            raise ValueError(
                f"Versão de schema não reconhecida: '{v}'. Esperado: '{VERSAO_SCHEMA_ATUAL}'"
            )
        return v


class ArquivoParametrosError(Exception):
    """O arquivo de parâmetros não pôde ser lido ou interpretado.

    Nunca cai para valores padrão — uma execução com pesos diferentes dos
    configurados pelo usuário seria um resultado plausível e errado.
    """


def gerar_nome_arquivo(cenario_id: str | int) -> str:
    sufixo = uuid.uuid4().hex[:8]
    return f"cenario_{cenario_id}_{sufixo}.json"


def caminho_absoluto(nome_arquivo: str) -> Path:
    return settings.caminho_cenarios / nome_arquivo


def salvar_parametros(parametros: ParametrosCenario) -> str:
    """Grava o JSON e retorna o nome do arquivo (relativo ao diretório de cenários)."""
    settings.garantir_diretorios()
    nome_arquivo = gerar_nome_arquivo(parametros.cenario_id)
    caminho = caminho_absoluto(nome_arquivo)
    caminho.write_text(
        json.dumps(parametros.model_dump(mode="json"), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return nome_arquivo


def atualizar_parametros(parametros: ParametrosCenario) -> str:
    """Grava uma **nova** versão dos parâmetros, nunca sobrescrevendo o arquivo antigo.

    Simulações já executadas guardam o caminho do arquivo que estava vigente
    no momento em que rodaram (`Simulacao.parametros_json_path`). Se editar
    sobrescrevesse o arquivo em disco, o histórico passaria a reportar
    parâmetros diferentes dos que realmente produziram aquele resultado.
    """
    return salvar_parametros(parametros)


def carregar_parametros(nome_arquivo: str) -> ParametrosCenario:
    caminho = caminho_absoluto(nome_arquivo)
    if not caminho.exists():
        raise ArquivoParametrosError(
            f"Arquivo de parâmetros não encontrado: '{nome_arquivo}'. "
            "A simulação não pode ser executada sem os pesos configurados."
        )
    try:
        conteudo = json.loads(caminho.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ArquivoParametrosError(
            f"Arquivo de parâmetros corrompido (JSON inválido): '{nome_arquivo}'"
        ) from exc

    try:
        return ParametrosCenario.model_validate(conteudo)
    except Exception as exc:  # noqa: BLE001 - qualquer falha de validação vira erro de arquivo
        raise ArquivoParametrosError(
            f"Arquivo de parâmetros inválido: '{nome_arquivo}': {exc}"
        ) from exc


def remover_parametros(nome_arquivo: str) -> None:
    caminho = caminho_absoluto(nome_arquivo)
    caminho.unlink(missing_ok=True)

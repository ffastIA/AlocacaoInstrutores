"""Contratos da API de cenários de simulação."""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator


class PesosObjetivoIn(BaseModel):
    maximizar_aproveitamento: float = Field(ge=0)
    antecipar_inicio: float = Field(ge=0)
    balancear_carga_instrutores: float = Field(ge=0)
    balancear_tipologias: float = Field(ge=0)

    @model_validator(mode="after")
    def _exige_algum_peso_positivo(self) -> "PesosObjetivoIn":
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


class PesosObjetivoOut(BaseModel):
    maximizar_aproveitamento: float
    antecipar_inicio: float
    balancear_carga_instrutores: float
    balancear_tipologias: float


class SolverConfigIn(BaseModel):
    time_limit_seg: int = Field(default=180, gt=0)
    num_workers: int = Field(default=8, gt=0)
    gap_relativo: float = Field(default=0.02, ge=0)
    seed: int = 42


class CenarioIn(BaseModel):
    nome: str = Field(min_length=1, max_length=200)
    descricao: str | None = None
    periodo_de: date
    periodo_ate: date
    projeto_ids: list[int] = Field(
        default_factory=list, description="Vazio significa todos os projetos"
    )
    permitir_compartilhamento: bool = False
    pesos_objetivo: PesosObjetivoIn
    solver: SolverConfigIn = Field(default_factory=SolverConfigIn)

    @model_validator(mode="after")
    def _valida_periodo(self) -> "CenarioIn":
        if self.periodo_ate < self.periodo_de:
            raise ValueError("Data final do período é anterior à data inicial")
        return self


class CenarioOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    descricao: str | None
    periodo_de: date
    periodo_ate: date
    projeto_ids: list[int]
    permitir_compartilhamento: bool
    pesos_objetivo: PesosObjetivoOut
    criado_em: datetime

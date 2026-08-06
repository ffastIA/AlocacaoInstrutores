"""Contratos da API de simulações."""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import Modalidade, StatusSimulacao, Turno


class ExecutarSimulacaoIn(BaseModel):
    cenario_id: int


class SimulacaoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    cenario_id: int
    status: StatusSimulacao
    iniciado_em: datetime
    concluido_em: datetime | None
    tempo_execucao_seg: float | None
    solver_status: str | None
    objetivo_valor: float | None
    mensagem_erro: str | None


class EncontroOut(BaseModel):
    data: date
    turno: Turno
    horas: float


class TurmaSugeridaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tipologia_id: int
    tipologia_nome: str
    instrutor_id: int
    instrutor_nome: str
    projeto_id: int
    modalidade: Modalidade
    turno: Turno
    semana_inicio: int
    data_inicio: date
    data_fim: date
    num_encontros: int
    carga_horaria_total: float
    encontros: list[EncontroOut] = []


class KpisOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    total_turmas_sugeridas: int
    horas_formacao_total: float
    slots_disponiveis_total: int
    pct_ociosidade: float
    indice_balanceamento_carga: float
    indice_balanceamento_tipologia: float
    slots_reposicao_sexta: int


class OportunidadeOut(BaseModel):
    tipologia_id: int
    tipologia_nome: str
    data_inicio: date
    total_turmas: int
    instrutor_ids: list[int]


class AgendaItemOut(BaseModel):
    origem: str = Field(description="'em_andamento' ou 'sugerida'")
    tipologia_id: int
    tipologia_nome: str
    modalidade: Modalidade
    turno: Turno
    data_inicio: date
    data_fim: date


class CapacidadeInstrutorOut(BaseModel):
    """Utilização de um instrutor no snapshot congelado desta simulação."""

    instrutor_id: int
    instrutor_nome: str
    projeto_id: int
    projeto_nome: str
    slots_disponiveis: int
    slots_ocupados: int
    utilizacao_percentual: float
    primeira_data_livre: date | None
    primeira_data_livre_por_slot: dict[Turno, date] = Field(
        description="Data de liberação de cada slot do instrutor, independentemente dos demais"
    )


class ComparacaoItemOut(BaseModel):
    simulacao_id: int
    cenario_id: int
    cenario_nome: str
    periodo_de: date
    periodo_ate: date
    permitir_compartilhamento: bool
    pesos_objetivo: dict[str, float]
    kpis: KpisOut


class ComparacaoOut(BaseModel):
    itens: list[ComparacaoItemOut]
    periodos_divergentes: bool

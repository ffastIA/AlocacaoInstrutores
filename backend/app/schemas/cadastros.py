"""Contratos dos cadastros de domínio."""

from datetime import date

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.enums import DIA_SEMANA_MAX, DIA_SEMANA_MIN, Modalidade, Turno


class _Orm(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# --------------------------------------------------------------------------
# Projetos
# --------------------------------------------------------------------------


class ProjetoIn(BaseModel):
    nome: str = Field(min_length=1, max_length=200)
    descricao: str | None = None
    ativo: bool = True


class ProjetoOut(_Orm):
    id: int
    nome: str
    descricao: str | None
    ativo: bool
    total_instrutores: int = 0


# --------------------------------------------------------------------------
# Tipologias
# --------------------------------------------------------------------------


class TipologiaIn(BaseModel):
    nome: str = Field(min_length=1, max_length=200)
    carga_horaria_total_horas: int | None = Field(default=None, ge=24, le=60)
    horas_por_encontro: float | None = Field(default=None, gt=0)
    descricao: str | None = None

    @model_validator(mode="after")
    def _validar_divisibilidade(self) -> "TipologiaIn":
        """A carga total precisa fechar em número inteiro de encontros."""
        if self.carga_horaria_total_horas is None or self.horas_por_encontro is None:
            return self
        encontros = self.carga_horaria_total_horas / self.horas_por_encontro
        if encontros != int(encontros):
            raise ValueError(
                f"Carga horária total ({self.carga_horaria_total_horas}h) não é múltiplo exato "
                f"das horas por encontro ({self.horas_por_encontro}h): "
                f"resultaria em {encontros:.2f} encontros"
            )
        return self


class TipologiaOut(_Orm):
    id: int
    nome: str
    carga_horaria_total_horas: int | None
    horas_por_encontro: float | None
    descricao: str | None
    configurada: bool
    num_encontros: int | None
    total_instrutores: int = 0


class TipologiaPendenteOut(_Orm):
    id: int
    nome: str
    total_instrutores: int = 0


# --------------------------------------------------------------------------
# Instrutores
# --------------------------------------------------------------------------


class TurnoDisponivelIn(BaseModel):
    turno: Turno
    carga_horaria_horas: float = Field(gt=0)


class TurnoDisponivelOut(_Orm):
    turno: Turno
    carga_horaria_horas: float


class InstrutorIn(BaseModel):
    nome: str = Field(min_length=1, max_length=200)
    projeto_id: int
    turnos: list[TurnoDisponivelIn] = Field(min_length=1)
    dias_semana: list[int] = Field(min_length=1)
    tipologia_ids: list[int] = Field(min_length=1)
    observacao: str | None = None
    ativo: bool = True

    @model_validator(mode="after")
    def _validar(self) -> "InstrutorIn":
        turnos = [t.turno for t in self.turnos]
        if len(turnos) != len(set(turnos)):
            raise ValueError("Turno informado mais de uma vez")

        for dia in self.dias_semana:
            if not DIA_SEMANA_MIN <= dia <= DIA_SEMANA_MAX:
                raise ValueError(
                    f"Dia da semana fora da faixa: {dia}. "
                    f"Aceito de {DIA_SEMANA_MIN} (segunda) a {DIA_SEMANA_MAX} (sexta)"
                )
        if len(self.dias_semana) != len(set(self.dias_semana)):
            raise ValueError("Dia da semana informado mais de uma vez")

        if len(self.tipologia_ids) != len(set(self.tipologia_ids)):
            raise ValueError("Tipologia informada mais de uma vez")
        return self


class InstrutorOut(_Orm):
    id: int
    nome: str
    projeto_id: int
    projeto_nome: str
    turnos: list[TurnoDisponivelOut]
    dias_semana: list[int]
    tipologias: list[str]
    observacao: str | None
    ativo: bool


# --------------------------------------------------------------------------
# Turmas em andamento
# --------------------------------------------------------------------------


class TurmaEmAndamentoIn(BaseModel):
    instrutor_id: int
    tipologia_id: int
    modalidade: Modalidade
    turno: Turno
    data_inicio: date
    data_fim_prevista: date
    codigo_turma: str | None = None

    @model_validator(mode="after")
    def _validar_datas(self) -> "TurmaEmAndamentoIn":
        if self.data_fim_prevista < self.data_inicio:
            raise ValueError("Data de término prevista é anterior à data de início")
        return self


class TurmaEmAndamentoOut(_Orm):
    id: int
    codigo_turma: str | None
    instrutor_id: int
    instrutor_nome: str
    tipologia_id: int
    tipologia_nome: str
    projeto_id: int
    modalidade: Modalidade
    turno: Turno
    data_inicio: date
    data_fim_prevista: date

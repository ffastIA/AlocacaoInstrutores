"""Modelo de dados do domínio.

Estrutura em três blocos:

1. **Cadastros** — projetos, instrutores (com turnos, dias e tipologias),
   tipologias e turmas em andamento. Alimentados por importação de planilha.
2. **Calendário** — datas não letivas. Persistidas na v1, mas ainda sem efeito
   sobre a geração de calendários.
3. **Simulação** — cenários, execuções e resultados. As turmas sugeridas são a
   saída do motor de otimização.
"""

from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy import (
    Enum as SAEnum,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import (
    DIA_SEMANA_MAX,
    DIA_SEMANA_MIN,
    Modalidade,
    StatusSimulacao,
    TipoDataNaoLetiva,
    Turno,
)


def _enum(enum_cls: type) -> SAEnum:
    """Enum persistido pelo valor, em VARCHAR.

    O SQLite não tem tipo enum nativo; gravar o valor (e não o nome) mantém a
    coluna legível ao inspecionar o banco diretamente.
    """
    return SAEnum(
        enum_cls,
        native_enum=False,
        values_callable=lambda e: [membro.value for membro in e],
        length=32,
    )


# --------------------------------------------------------------------------
# Cadastros
# --------------------------------------------------------------------------


class Projeto(Base):
    __tablename__ = "projetos"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(200), nullable=False, unique=True, index=True)
    descricao: Mapped[str | None] = mapped_column(Text)
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())

    instrutores: Mapped[list["Instrutor"]] = relationship(back_populates="projeto")


class Tipologia(Base):
    """Curso ofertável.

    O catálogo é derivado das habilidades dos instrutores importados. Uma
    tipologia nasce sem carga horária e fica pendente até ser configurada —
    enquanto houver pendência no escopo, a simulação é bloqueada.
    """

    __tablename__ = "tipologias"
    __table_args__ = (
        CheckConstraint(
            "carga_horaria_total_horas IS NULL "
            "OR (carga_horaria_total_horas >= 24 AND carga_horaria_total_horas <= 60)",
            name="ck_tipologia_carga_total_faixa",
        ),
        CheckConstraint(
            "horas_por_encontro IS NULL OR horas_por_encontro > 0",
            name="ck_tipologia_horas_encontro_positivo",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(200), nullable=False, unique=True, index=True)
    carga_horaria_total_horas: Mapped[int | None] = mapped_column(Integer)
    horas_por_encontro: Mapped[float | None] = mapped_column(Float)
    descricao: Mapped[str | None] = mapped_column(Text)
    criado_em: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())

    instrutores: Mapped[list["InstrutorTipologia"]] = relationship(back_populates="tipologia")

    @property
    def configurada(self) -> bool:
        """Indica se a tipologia já pode gerar turmas."""
        return self.carga_horaria_total_horas is not None and self.horas_por_encontro is not None

    @property
    def num_encontros(self) -> int | None:
        """Número de encontros derivado da carga horária."""
        if not self.configurada:
            return None
        return int(self.carga_horaria_total_horas / self.horas_por_encontro)


class Instrutor(Base):
    __tablename__ = "instrutores"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(200), nullable=False, unique=True, index=True)
    projeto_id: Mapped[int] = mapped_column(
        ForeignKey("projetos.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    observacao: Mapped[str | None] = mapped_column(Text)
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())

    projeto: Mapped[Projeto] = relationship(back_populates="instrutores")
    turnos: Mapped[list["InstrutorTurno"]] = relationship(
        back_populates="instrutor", cascade="all, delete-orphan"
    )
    dias: Mapped[list["InstrutorDia"]] = relationship(
        back_populates="instrutor", cascade="all, delete-orphan"
    )
    tipologias: Mapped[list["InstrutorTipologia"]] = relationship(
        back_populates="instrutor", cascade="all, delete-orphan"
    )


class InstrutorTurno(Base):
    """Disponibilidade do instrutor em um turno, com sua capacidade horária.

    A capacidade é por turno porque o limite de 4 turmas/dia só é coerente se
    mais de uma turma couber no mesmo turno: duas de 2h cabem num turno de 4h,
    mas não num de 3h.
    """

    __tablename__ = "instrutor_turno"
    __table_args__ = (
        UniqueConstraint("instrutor_id", "turno", name="uq_instrutor_turno"),
        CheckConstraint("carga_horaria_horas > 0", name="ck_instrutor_turno_carga_positiva"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    instrutor_id: Mapped[int] = mapped_column(
        ForeignKey("instrutores.id", ondelete="CASCADE"), nullable=False, index=True
    )
    turno: Mapped[Turno] = mapped_column(_enum(Turno), nullable=False)
    carga_horaria_horas: Mapped[float] = mapped_column(Float, nullable=False)

    instrutor: Mapped[Instrutor] = relationship(back_populates="turnos")


class InstrutorDia(Base):
    """Dia da semana disponível: 2 = segunda ... 6 = sexta.

    O dia 6 é aceito e armazenado, mas conta apenas como capacidade de
    reposição — nunca recebe turma regular.
    """

    __tablename__ = "instrutor_dia"
    __table_args__ = (
        UniqueConstraint("instrutor_id", "dia_semana", name="uq_instrutor_dia"),
        CheckConstraint(
            f"dia_semana >= {DIA_SEMANA_MIN} AND dia_semana <= {DIA_SEMANA_MAX}",
            name="ck_instrutor_dia_faixa",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    instrutor_id: Mapped[int] = mapped_column(
        ForeignKey("instrutores.id", ondelete="CASCADE"), nullable=False, index=True
    )
    dia_semana: Mapped[int] = mapped_column(Integer, nullable=False)

    instrutor: Mapped[Instrutor] = relationship(back_populates="dias")


class InstrutorTipologia(Base):
    """Habilidade do instrutor. É esta relação que define o que é ofertável."""

    __tablename__ = "instrutor_tipologia"
    __table_args__ = (
        UniqueConstraint("instrutor_id", "tipologia_id", name="uq_instrutor_tipologia"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    instrutor_id: Mapped[int] = mapped_column(
        ForeignKey("instrutores.id", ondelete="CASCADE"), nullable=False, index=True
    )
    tipologia_id: Mapped[int] = mapped_column(
        ForeignKey("tipologias.id", ondelete="CASCADE"), nullable=False, index=True
    )

    instrutor: Mapped[Instrutor] = relationship(back_populates="tipologias")
    tipologia: Mapped[Tipologia] = relationship(back_populates="instrutores")


class TurmaEmAndamento(Base):
    """Turma já em execução.

    Não é decisão do solver: consome capacidade do instrutor até sua data de
    término, e é isso que torna a disponibilidade progressiva ao longo do
    período simulado.
    """

    __tablename__ = "turmas_em_andamento"
    __table_args__ = (
        CheckConstraint("data_fim_prevista >= data_inicio", name="ck_turma_andamento_datas"),
        Index("ix_turma_andamento_periodo", "data_inicio", "data_fim_prevista"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    codigo_turma: Mapped[str | None] = mapped_column(String(100))
    instrutor_id: Mapped[int] = mapped_column(
        ForeignKey("instrutores.id", ondelete="CASCADE"), nullable=False, index=True
    )
    tipologia_id: Mapped[int] = mapped_column(
        ForeignKey("tipologias.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    projeto_id: Mapped[int] = mapped_column(
        ForeignKey("projetos.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    modalidade: Mapped[Modalidade] = mapped_column(_enum(Modalidade), nullable=False)
    turno: Mapped[Turno] = mapped_column(_enum(Turno), nullable=False)
    data_inicio: Mapped[date] = mapped_column(Date, nullable=False)
    data_fim_prevista: Mapped[date] = mapped_column(Date, nullable=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())

    instrutor: Mapped[Instrutor] = relationship()
    tipologia: Mapped[Tipologia] = relationship()
    projeto: Mapped[Projeto] = relationship()


# --------------------------------------------------------------------------
# Calendário
# --------------------------------------------------------------------------


class DataNaoLetiva(Base):
    """Feriado, recesso ou período de férias.

    Importado e persistido na v1, porém ainda **sem efeito** sobre a geração de
    calendários — a regra de deslocamento de encontros está em aberto.

    `projeto_id` nulo significa que o intervalo vale para todos os projetos.
    """

    __tablename__ = "datas_nao_letivas"
    __table_args__ = (
        CheckConstraint("data_fim >= data_inicio", name="ck_data_nao_letiva_intervalo"),
        Index("ix_data_nao_letiva_intervalo", "data_inicio", "data_fim"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    data_inicio: Mapped[date] = mapped_column(Date, nullable=False)
    data_fim: Mapped[date] = mapped_column(Date, nullable=False)
    descricao: Mapped[str] = mapped_column(String(300), nullable=False)
    tipo: Mapped[TipoDataNaoLetiva] = mapped_column(
        _enum(TipoDataNaoLetiva), nullable=False, default=TipoDataNaoLetiva.FERIADO
    )
    projeto_id: Mapped[int | None] = mapped_column(
        ForeignKey("projetos.id", ondelete="CASCADE"), index=True
    )
    criado_em: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())

    projeto: Mapped[Projeto | None] = relationship()


# --------------------------------------------------------------------------
# Simulação
# --------------------------------------------------------------------------


class Cenario(Base):
    """Configuração de uma simulação.

    Os pesos do objetivo ficam no arquivo JSON apontado por
    `parametros_json_path`; aqui ficam apenas os metadados consultáveis.
    """

    __tablename__ = "cenarios"
    __table_args__ = (
        CheckConstraint("periodo_ate >= periodo_de", name="ck_cenario_periodo"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(200), nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text)
    parametros_json_path: Mapped[str] = mapped_column(String(500), nullable=False)
    periodo_de: Mapped[date] = mapped_column(Date, nullable=False)
    periodo_ate: Mapped[date] = mapped_column(Date, nullable=False)
    permitir_compartilhamento: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    criado_em: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())

    projetos: Mapped[list["CenarioProjeto"]] = relationship(
        back_populates="cenario", cascade="all, delete-orphan"
    )
    simulacoes: Mapped[list["Simulacao"]] = relationship(back_populates="cenario")


class CenarioProjeto(Base):
    """Escopo de projetos do cenário. Vazio significa todos os projetos."""

    __tablename__ = "cenario_projeto"
    __table_args__ = (UniqueConstraint("cenario_id", "projeto_id", name="uq_cenario_projeto"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    cenario_id: Mapped[int] = mapped_column(
        ForeignKey("cenarios.id", ondelete="CASCADE"), nullable=False, index=True
    )
    projeto_id: Mapped[int] = mapped_column(
        ForeignKey("projetos.id", ondelete="CASCADE"), nullable=False, index=True
    )

    cenario: Mapped[Cenario] = relationship(back_populates="projetos")
    projeto: Mapped[Projeto] = relationship()


class Simulacao(Base):
    """Uma execução de um cenário."""

    __tablename__ = "simulacoes"
    __table_args__ = (Index("ix_simulacao_cenario_iniciado", "cenario_id", "iniciado_em"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    cenario_id: Mapped[int] = mapped_column(
        ForeignKey("cenarios.id", ondelete="CASCADE"), nullable=False, index=True
    )
    status: Mapped[StatusSimulacao] = mapped_column(
        _enum(StatusSimulacao), nullable=False, default=StatusSimulacao.PENDENTE, index=True
    )
    iniciado_em: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    concluido_em: Mapped[datetime | None] = mapped_column(DateTime)
    tempo_execucao_seg: Mapped[float | None] = mapped_column(Float)
    solver_status: Mapped[str | None] = mapped_column(String(50))
    objetivo_valor: Mapped[float | None] = mapped_column(Float)
    mensagem_erro: Mapped[str | None] = mapped_column(Text)
    log_path: Mapped[str | None] = mapped_column(String(500))

    cenario: Mapped[Cenario] = relationship(back_populates="simulacoes")
    turmas_sugeridas: Mapped[list["TurmaSugerida"]] = relationship(
        back_populates="simulacao", cascade="all, delete-orphan"
    )
    kpis: Mapped["ResultadoKpis | None"] = relationship(
        back_populates="simulacao", cascade="all, delete-orphan", uselist=False
    )
    snapshots: Mapped[list["SnapshotCapacidade"]] = relationship(
        back_populates="simulacao", cascade="all, delete-orphan"
    )


class TurmaSugerida(Base):
    """Saída da simulação: uma turma que pode ser aberta.

    É sugestão, não compromisso — a decisão de abrir continua com a equipe.
    """

    __tablename__ = "turmas_sugeridas"
    __table_args__ = (
        Index("ix_turma_sugerida_sim_tipologia", "simulacao_id", "tipologia_id"),
        Index("ix_turma_sugerida_sim_inicio", "simulacao_id", "data_inicio"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    simulacao_id: Mapped[int] = mapped_column(
        ForeignKey("simulacoes.id", ondelete="CASCADE"), nullable=False, index=True
    )
    tipologia_id: Mapped[int] = mapped_column(
        ForeignKey("tipologias.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    instrutor_id: Mapped[int] = mapped_column(
        ForeignKey("instrutores.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    projeto_id: Mapped[int] = mapped_column(
        ForeignKey("projetos.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    modalidade: Mapped[Modalidade] = mapped_column(_enum(Modalidade), nullable=False)
    turno: Mapped[Turno] = mapped_column(_enum(Turno), nullable=False)
    semana_inicio: Mapped[int] = mapped_column(Integer, nullable=False)
    data_inicio: Mapped[date] = mapped_column(Date, nullable=False)
    data_fim: Mapped[date] = mapped_column(Date, nullable=False)
    num_encontros: Mapped[int] = mapped_column(Integer, nullable=False)
    carga_horaria_total: Mapped[float] = mapped_column(Float, nullable=False)

    simulacao: Mapped[Simulacao] = relationship(back_populates="turmas_sugeridas")
    tipologia: Mapped[Tipologia] = relationship()
    instrutor: Mapped[Instrutor] = relationship()
    projeto: Mapped[Projeto] = relationship()
    encontros: Mapped[list["TurmaSugeridaEncontro"]] = relationship(
        back_populates="turma", cascade="all, delete-orphan"
    )


class TurmaSugeridaEncontro(Base):
    """Um encontro do calendário de uma turma sugerida."""

    __tablename__ = "turma_sugerida_encontro"
    __table_args__ = (Index("ix_encontro_turma_data", "turma_sugerida_id", "data"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    turma_sugerida_id: Mapped[int] = mapped_column(
        ForeignKey("turmas_sugeridas.id", ondelete="CASCADE"), nullable=False, index=True
    )
    data: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    turno: Mapped[Turno] = mapped_column(_enum(Turno), nullable=False)
    horas: Mapped[float] = mapped_column(Float, nullable=False)

    turma: Mapped[TurmaSugerida] = relationship(back_populates="encontros")


class ResultadoKpis(Base):
    """Indicadores agregados de uma simulação."""

    __tablename__ = "resultado_kpis"

    id: Mapped[int] = mapped_column(primary_key=True)
    simulacao_id: Mapped[int] = mapped_column(
        ForeignKey("simulacoes.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    total_turmas_sugeridas: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    horas_formacao_total: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    horas_disponiveis_total: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    pct_ociosidade: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    indice_balanceamento_carga: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    indice_balanceamento_tipologia: Mapped[float] = mapped_column(
        Float, nullable=False, default=0.0
    )
    horas_reposicao_sexta: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    simulacao: Mapped[Simulacao] = relationship(back_populates="kpis")


class SnapshotCapacidade(Base):
    """Capacidade de um instrutor congelada no momento da execução.

    Sem isso, uma simulação consultada semanas depois seria interpretada contra
    dados que já mudaram, tornando o resultado inexplicável.
    """

    __tablename__ = "snapshot_capacidade"
    __table_args__ = (
        UniqueConstraint("simulacao_id", "instrutor_id", name="uq_snapshot_simulacao_instrutor"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    simulacao_id: Mapped[int] = mapped_column(
        ForeignKey("simulacoes.id", ondelete="CASCADE"), nullable=False, index=True
    )
    instrutor_id: Mapped[int] = mapped_column(
        ForeignKey("instrutores.id", ondelete="CASCADE"), nullable=False, index=True
    )
    horas_disponiveis: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    horas_alocadas: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    primeira_data_livre: Mapped[date | None] = mapped_column(Date)

    simulacao: Mapped[Simulacao] = relationship(back_populates="snapshots")
    instrutor: Mapped[Instrutor] = relationship()

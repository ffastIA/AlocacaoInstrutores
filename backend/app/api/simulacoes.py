"""Execução de simulações, consulta de resultados, comparação e exportação."""

import json
from datetime import date

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db.session import get_db
from app.models import (
    Cenario,
    Instrutor,
    OportunidadeSimulacao,
    ResultadoKpis,
    Simulacao,
    SnapshotCapacidade,
    StatusSimulacao,
    TurmaEmAndamento,
    TurmaSugerida,
    Turno,
)
from app.schemas.simulacoes import (
    AgendaItemOut,
    CapacidadeInstrutorOut,
    ComparacaoItemOut,
    ComparacaoOut,
    ExecutarSimulacaoIn,
    KpisOut,
    OportunidadeOut,
    SimulacaoOut,
    TurmaSugeridaOut,
)
from app.services.cenarios.parametros import carregar_parametros
from app.services.exportacao.planilha_resultado import gerar_planilha_resultado
from app.services.simulacao.executor import executar_simulacao
from app.services.simulacao.repositorio import (
    carregar_instrutores,
    listar_tipologias_pendentes_no_escopo,
)

router = APIRouter(prefix="/simulacoes", tags=["simulações"])


def _obter_ou_404(db: Session, simulacao_id: int) -> Simulacao:
    simulacao = db.get(Simulacao, simulacao_id)
    if simulacao is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Simulação {simulacao_id} não encontrada",
        )
    return simulacao


def _simulacao_out(simulacao: Simulacao) -> SimulacaoOut:
    return SimulacaoOut.model_validate(simulacao)


@router.post(
    "/executar",
    response_model=SimulacaoOut,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Dispara a execução de um cenário",
    description=(
        "Cria o registro da simulação e inicia o processamento em segundo plano, "
        "retornando imediatamente. Consulte o status em GET /simulacoes/{id}."
    ),
)
def executar_simulacao_endpoint(
    dados: ExecutarSimulacaoIn,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
) -> SimulacaoOut:
    cenario = db.get(Cenario, dados.cenario_id)
    if cenario is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cenário {dados.cenario_id} não encontrado",
        )

    escopo_ids = [cp.projeto_id for cp in cenario.projetos]
    instrutores = carregar_instrutores(
        db, None if (cenario.permitir_compartilhamento or not escopo_ids) else escopo_ids
    )
    if not instrutores:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=(
                "Nenhum instrutor no escopo deste cenário — não há capacidade a simular. "
                "Revise o escopo de projetos ou importe instrutores."
            ),
        )

    pendentes = listar_tipologias_pendentes_no_escopo(db, instrutores)
    if pendentes:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=(
                "Tipologias pendentes de configuração de carga horária: "
                + ", ".join(pendentes)
                + ". Configure-as antes de simular."
            ),
        )

    simulacao = Simulacao(
        cenario_id=cenario.id,
        status=StatusSimulacao.PENDENTE,
        # Congela o snapshot dos parâmetros vigentes no disparo — editar o
        # cenário depois não deve alterar o que esta simulação reporta ter usado.
        parametros_json_path=cenario.parametros_json_path,
    )
    db.add(simulacao)
    db.commit()

    background_tasks.add_task(executar_simulacao, simulacao.id)

    return _simulacao_out(simulacao)


@router.get("", response_model=list[SimulacaoOut], summary="Histórico de simulações")
def listar_simulacoes(
    cenario_id: int | None = Query(default=None),
    pagina: int = Query(default=1, ge=1),
    tamanho_pagina: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> list[SimulacaoOut]:
    consulta = select(Simulacao).order_by(Simulacao.iniciado_em.desc())
    if cenario_id is not None:
        consulta = consulta.where(Simulacao.cenario_id == cenario_id)
    consulta = consulta.offset((pagina - 1) * tamanho_pagina).limit(tamanho_pagina)

    return [_simulacao_out(s) for s in db.scalars(consulta).all()]


@router.get(
    "/comparar",
    response_model=ComparacaoOut,
    summary="Compara os KPIs de duas ou mais simulações lado a lado",
    description=(
        "Registrada antes de /{simulacao_id} de propósito: sem essa ordem, "
        "'comparar' seria interpretado como um identificador de simulação."
    ),
)
def comparar_simulacoes(
    ids: str = Query(description="Identificadores separados por vírgula, ex.: 1,2,3"),
    db: Session = Depends(get_db),
) -> ComparacaoOut:
    try:
        simulacao_ids = [int(i) for i in ids.split(",") if i.strip()]
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Identificadores inválidos — use números separados por vírgula",
        ) from exc

    if len(simulacao_ids) < 2:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Informe ao menos duas simulações para comparar",
        )

    itens = []
    for sid in simulacao_ids:
        simulacao = db.get(Simulacao, sid)
        if simulacao is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"Simulação {sid} não encontrada"
            )
        if simulacao.status != StatusSimulacao.CONCLUIDA:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail=(
                    f"Simulação {sid} ainda não está concluída (status: {simulacao.status.value})"
                ),
            )
        if simulacao.kpis is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail=f"Simulação {sid} não tem KPIs calculados",
            )

        parametros = carregar_parametros(simulacao.parametros_json_path)
        itens.append(
            ComparacaoItemOut(
                simulacao_id=simulacao.id,
                cenario_id=simulacao.cenario_id,
                cenario_nome=simulacao.cenario.nome,
                periodo_de=simulacao.cenario.periodo_de,
                periodo_ate=simulacao.cenario.periodo_ate,
                permitir_compartilhamento=simulacao.cenario.permitir_compartilhamento,
                pesos_objetivo=parametros.pesos_objetivo.model_dump(),
                kpis=KpisOut.model_validate(simulacao.kpis),
            )
        )

    periodos = {(item.periodo_de, item.periodo_ate) for item in itens}
    return ComparacaoOut(itens=itens, periodos_divergentes=len(periodos) > 1)


@router.get("/{simulacao_id}", response_model=SimulacaoOut)
def obter_simulacao(simulacao_id: int, db: Session = Depends(get_db)) -> SimulacaoOut:
    return _simulacao_out(_obter_ou_404(db, simulacao_id))


@router.get("/{simulacao_id}/turmas-sugeridas", response_model=list[TurmaSugeridaOut])
def listar_turmas_sugeridas(
    simulacao_id: int, db: Session = Depends(get_db)
) -> list[TurmaSugeridaOut]:
    _obter_ou_404(db, simulacao_id)

    turmas = db.scalars(
        select(TurmaSugerida)
        .where(TurmaSugerida.simulacao_id == simulacao_id)
        .options(selectinload(TurmaSugerida.encontros))
        .order_by(TurmaSugerida.data_inicio)
    ).all()

    return [
        TurmaSugeridaOut(
            id=t.id,
            tipologia_id=t.tipologia_id,
            tipologia_nome=t.tipologia.nome,
            instrutor_id=t.instrutor_id,
            instrutor_nome=t.instrutor.nome,
            projeto_id=t.projeto_id,
            modalidade=t.modalidade,
            turno=t.turno,
            semana_inicio=t.semana_inicio,
            data_inicio=t.data_inicio,
            data_fim=t.data_fim,
            num_encontros=t.num_encontros,
            carga_horaria_total=t.carga_horaria_total,
            encontros=[{"data": e.data, "turno": e.turno, "horas": e.horas} for e in t.encontros],
        )
        for t in turmas
    ]


@router.get("/{simulacao_id}/kpis", response_model=KpisOut)
def obter_kpis(simulacao_id: int, db: Session = Depends(get_db)) -> KpisOut:
    _obter_ou_404(db, simulacao_id)

    kpis = db.scalar(select(ResultadoKpis).where(ResultadoKpis.simulacao_id == simulacao_id))
    if kpis is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Simulação {simulacao_id} ainda não tem KPIs calculados",
        )
    return KpisOut.model_validate(kpis)


@router.get(
    "/{simulacao_id}/capacidade-instrutores",
    response_model=list[CapacidadeInstrutorOut],
    summary="Utilização de cada instrutor no snapshot desta simulação",
    description=(
        "Slots disponíveis, ocupados e primeira data livre (agregada e por slot), "
        "congelados no momento da execução — não refletem alterações feitas nos "
        "dados depois."
    ),
)
def obter_capacidade_instrutores(
    simulacao_id: int,
    projeto_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[CapacidadeInstrutorOut]:
    _obter_ou_404(db, simulacao_id)

    consulta = select(SnapshotCapacidade).where(SnapshotCapacidade.simulacao_id == simulacao_id)
    if projeto_id is not None:
        consulta = consulta.join(Instrutor).where(Instrutor.projeto_id == projeto_id)

    return [
        CapacidadeInstrutorOut(
            instrutor_id=s.instrutor_id,
            instrutor_nome=s.instrutor.nome,
            projeto_id=s.instrutor.projeto_id,
            projeto_nome=s.instrutor.projeto.nome,
            slots_disponiveis=s.slots_disponiveis,
            slots_ocupados=s.slots_ocupados,
            utilizacao_percentual=(
                round(s.slots_ocupados / s.slots_disponiveis * 100, 1)
                if s.slots_disponiveis > 0
                else 0.0
            ),
            primeira_data_livre=s.primeira_data_livre,
            primeira_data_livre_por_slot={
                Turno(turno): date.fromisoformat(valor)
                for turno, valor in json.loads(s.primeira_data_livre_por_slot_json).items()
            },
        )
        for s in db.scalars(consulta).all()
    ]


@router.get(
    "/{simulacao_id}/oportunidades",
    response_model=list[OportunidadeOut],
    summary="Mapa de oportunidades: o que pode ser aberto, e a partir de quando",
    description=(
        "Reflete todas as candidatas geradas — não apenas as escolhidas pelo "
        "solver — organizadas por tipologia e data de início, em ordem cronológica."
    ),
)
def obter_oportunidades(
    simulacao_id: int,
    tipologia_id: int | None = Query(default=None),
    instrutor_id: int | None = Query(default=None),
    data_de: str | None = Query(default=None),
    data_ate: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[OportunidadeOut]:
    _obter_ou_404(db, simulacao_id)

    consulta = select(OportunidadeSimulacao).where(
        OportunidadeSimulacao.simulacao_id == simulacao_id
    )
    if tipologia_id is not None:
        consulta = consulta.where(OportunidadeSimulacao.tipologia_id == tipologia_id)
    if data_de is not None:
        consulta = consulta.where(OportunidadeSimulacao.data_inicio >= data_de)
    if data_ate is not None:
        consulta = consulta.where(OportunidadeSimulacao.data_inicio <= data_ate)
    consulta = consulta.order_by(
        OportunidadeSimulacao.data_inicio, OportunidadeSimulacao.tipologia_id
    )

    resultado = []
    for o in db.scalars(consulta).all():
        instrutor_ids = [int(i) for i in o.instrutor_ids_csv.split(",") if i]
        if instrutor_id is not None and instrutor_id not in instrutor_ids:
            continue
        resultado.append(
            OportunidadeOut(
                tipologia_id=o.tipologia_id,
                tipologia_nome=o.tipologia.nome,
                data_inicio=o.data_inicio,
                total_turmas=o.total_turmas,
                instrutor_ids=instrutor_ids,
            )
        )
    return resultado


@router.get(
    "/{simulacao_id}/agenda/{instrutor_id}",
    response_model=list[AgendaItemOut],
    summary="Agenda de um instrutor: turmas em andamento e sugeridas",
)
def obter_agenda_instrutor(
    simulacao_id: int, instrutor_id: int, db: Session = Depends(get_db)
) -> list[AgendaItemOut]:
    _obter_ou_404(db, simulacao_id)
    if db.get(Instrutor, instrutor_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Instrutor {instrutor_id} não encontrado",
        )

    itens = [
        AgendaItemOut(
            origem="em_andamento",
            tipologia_id=t.tipologia_id,
            tipologia_nome=t.tipologia.nome,
            modalidade=t.modalidade,
            turno=t.turno,
            data_inicio=t.data_inicio,
            data_fim=t.data_fim_prevista,
        )
        for t in db.scalars(
            select(TurmaEmAndamento).where(TurmaEmAndamento.instrutor_id == instrutor_id)
        ).all()
    ]

    itens += [
        AgendaItemOut(
            origem="sugerida",
            tipologia_id=t.tipologia_id,
            tipologia_nome=t.tipologia.nome,
            modalidade=t.modalidade,
            turno=t.turno,
            data_inicio=t.data_inicio,
            data_fim=t.data_fim,
        )
        for t in db.scalars(
            select(TurmaSugerida).where(
                TurmaSugerida.simulacao_id == simulacao_id,
                TurmaSugerida.instrutor_id == instrutor_id,
            )
        ).all()
    ]

    return sorted(itens, key=lambda i: i.data_inicio)


TIPO_XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


@router.get(
    "/{simulacao_id}/exportar",
    summary="Exporta o resultado em planilha",
    description="Turmas sugeridas, KPIs e parâmetros do cenário. Só para simulações concluídas.",
    response_class=Response,
)
def exportar_simulacao(simulacao_id: int, db: Session = Depends(get_db)) -> Response:
    simulacao = _obter_ou_404(db, simulacao_id)
    if simulacao.status != StatusSimulacao.CONCLUIDA:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=(
                f"Simulação {simulacao_id} ainda não está concluída "
                f"(status: {simulacao.status.value}) — a exportação exige um resultado pronto."
            ),
        )

    conteudo, nome_arquivo = gerar_planilha_resultado(db, simulacao)
    return Response(
        content=conteudo,
        media_type=TIPO_XLSX,
        headers={"Content-Disposition": f'attachment; filename="{nome_arquivo}"'},
    )

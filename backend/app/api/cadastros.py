"""CRUD dos cadastros de domínio.

Complementa a importação de planilhas: permite ajuste pontual sem exigir
reeditar e reimportar o arquivo inteiro.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import (
    Instrutor,
    InstrutorDia,
    InstrutorTipologia,
    InstrutorTurno,
    Projeto,
    Tipologia,
    TurmaEmAndamento,
)
from app.schemas.cadastros import (
    InstrutorIn,
    InstrutorOut,
    ProjetoIn,
    ProjetoOut,
    TipologiaIn,
    TipologiaOut,
    TipologiaPendenteOut,
    TurmaEmAndamentoIn,
    TurmaEmAndamentoOut,
    TurnoDisponivelOut,
)
from app.services.importacao.parser_tipologias import listar_pendentes

router = APIRouter(tags=["cadastros"])


def _obter_ou_404(db: Session, modelo: type, id_: int, rotulo: str):
    objeto = db.get(modelo, id_)
    if objeto is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"{rotulo} {id_} não encontrado"
        )
    return objeto


# --------------------------------------------------------------------------
# Projetos
# --------------------------------------------------------------------------


def _projeto_out(db: Session, projeto: Projeto) -> ProjetoOut:
    total = db.scalar(
        select(func.count(Instrutor.id)).where(Instrutor.projeto_id == projeto.id)
    )
    return ProjetoOut(
        id=projeto.id,
        nome=projeto.nome,
        descricao=projeto.descricao,
        ativo=projeto.ativo,
        total_instrutores=total or 0,
    )


@router.get("/projetos", response_model=list[ProjetoOut])
def listar_projetos(db: Session = Depends(get_db)) -> list[ProjetoOut]:
    projetos = db.scalars(select(Projeto).order_by(Projeto.nome)).all()
    return [_projeto_out(db, p) for p in projetos]


@router.post("/projetos", response_model=ProjetoOut, status_code=status.HTTP_201_CREATED)
def criar_projeto(dados: ProjetoIn, db: Session = Depends(get_db)) -> ProjetoOut:
    if db.scalar(select(Projeto).where(Projeto.nome == dados.nome)):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Já existe um projeto com o nome '{dados.nome}'",
        )
    projeto = Projeto(**dados.model_dump())
    db.add(projeto)
    db.commit()
    return _projeto_out(db, projeto)


@router.put("/projetos/{projeto_id}", response_model=ProjetoOut)
def atualizar_projeto(
    projeto_id: int, dados: ProjetoIn, db: Session = Depends(get_db)
) -> ProjetoOut:
    projeto = _obter_ou_404(db, Projeto, projeto_id, "Projeto")
    existente = db.scalar(select(Projeto).where(Projeto.nome == dados.nome))
    if existente and existente.id != projeto_id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Já existe um projeto com o nome '{dados.nome}'",
        )
    for campo, valor in dados.model_dump().items():
        setattr(projeto, campo, valor)
    db.commit()
    return _projeto_out(db, projeto)


@router.delete("/projetos/{projeto_id}", status_code=status.HTTP_204_NO_CONTENT)
def remover_projeto(projeto_id: int, db: Session = Depends(get_db)) -> None:
    projeto = _obter_ou_404(db, Projeto, projeto_id, "Projeto")
    vinculados = db.scalar(
        select(func.count(Instrutor.id)).where(Instrutor.projeto_id == projeto_id)
    )
    if vinculados:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"O projeto tem {vinculados} instrutor(es) vinculado(s) e não pode ser removido",
        )
    db.delete(projeto)
    db.commit()


# --------------------------------------------------------------------------
# Tipologias
# --------------------------------------------------------------------------


def _contar_instrutores_tipologia(db: Session, tipologia_id: int) -> int:
    return (
        db.scalar(
            select(func.count(InstrutorTipologia.id)).where(
                InstrutorTipologia.tipologia_id == tipologia_id
            )
        )
        or 0
    )


def _tipologia_out(db: Session, tipologia: Tipologia) -> TipologiaOut:
    return TipologiaOut(
        id=tipologia.id,
        nome=tipologia.nome,
        carga_horaria_total_horas=tipologia.carga_horaria_total_horas,
        horas_por_encontro=tipologia.horas_por_encontro,
        descricao=tipologia.descricao,
        configurada=tipologia.configurada,
        num_encontros=tipologia.num_encontros,
        total_instrutores=_contar_instrutores_tipologia(db, tipologia.id),
    )


@router.get("/tipologias", response_model=list[TipologiaOut])
def listar_tipologias(db: Session = Depends(get_db)) -> list[TipologiaOut]:
    tipologias = db.scalars(select(Tipologia).order_by(Tipologia.nome)).all()
    return [_tipologia_out(db, t) for t in tipologias]


@router.get(
    "/tipologias/pendentes",
    response_model=list[TipologiaPendenteOut],
    summary="Tipologias que bloqueiam a simulação",
    description="Tipologias derivadas da planilha que ainda não têm carga horária configurada.",
)
def listar_tipologias_pendentes(db: Session = Depends(get_db)) -> list[TipologiaPendenteOut]:
    return [
        TipologiaPendenteOut(
            id=t.id, nome=t.nome, total_instrutores=_contar_instrutores_tipologia(db, t.id)
        )
        for t in listar_pendentes(db)
    ]


@router.post("/tipologias", response_model=TipologiaOut, status_code=status.HTTP_201_CREATED)
def criar_tipologia(dados: TipologiaIn, db: Session = Depends(get_db)) -> TipologiaOut:
    if db.scalar(select(Tipologia).where(Tipologia.nome == dados.nome)):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Já existe uma tipologia com o nome '{dados.nome}'",
        )
    tipologia = Tipologia(**dados.model_dump())
    db.add(tipologia)
    db.commit()
    return _tipologia_out(db, tipologia)


@router.put("/tipologias/{tipologia_id}", response_model=TipologiaOut)
def atualizar_tipologia(
    tipologia_id: int, dados: TipologiaIn, db: Session = Depends(get_db)
) -> TipologiaOut:
    tipologia = _obter_ou_404(db, Tipologia, tipologia_id, "Tipologia")
    existente = db.scalar(select(Tipologia).where(Tipologia.nome == dados.nome))
    if existente and existente.id != tipologia_id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Já existe uma tipologia com o nome '{dados.nome}'",
        )
    for campo, valor in dados.model_dump().items():
        setattr(tipologia, campo, valor)
    db.commit()
    return _tipologia_out(db, tipologia)


@router.delete("/tipologias/{tipologia_id}", status_code=status.HTTP_204_NO_CONTENT)
def remover_tipologia(tipologia_id: int, db: Session = Depends(get_db)) -> None:
    tipologia = _obter_ou_404(db, Tipologia, tipologia_id, "Tipologia")
    db.delete(tipologia)
    db.commit()


# --------------------------------------------------------------------------
# Instrutores
# --------------------------------------------------------------------------


def _instrutor_out(instrutor: Instrutor) -> InstrutorOut:
    return InstrutorOut(
        id=instrutor.id,
        nome=instrutor.nome,
        projeto_id=instrutor.projeto_id,
        projeto_nome=instrutor.projeto.nome,
        turnos=[
            TurnoDisponivelOut(turno=t.turno, carga_horaria_horas=t.carga_horaria_horas)
            for t in sorted(instrutor.turnos, key=lambda t: t.turno.value)
        ],
        dias_semana=sorted(d.dia_semana for d in instrutor.dias),
        tipologias=sorted(v.tipologia.nome for v in instrutor.tipologias),
        observacao=instrutor.observacao,
        ativo=instrutor.ativo,
    )


@router.get("/instrutores", response_model=list[InstrutorOut])
def listar_instrutores(
    projeto_id: int | None = Query(default=None),
    tipologia_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[InstrutorOut]:
    consulta = select(Instrutor).order_by(Instrutor.nome)
    if projeto_id is not None:
        consulta = consulta.where(Instrutor.projeto_id == projeto_id)
    if tipologia_id is not None:
        consulta = consulta.join(InstrutorTipologia).where(
            InstrutorTipologia.tipologia_id == tipologia_id
        )
    return [_instrutor_out(i) for i in db.scalars(consulta).all()]


@router.get("/instrutores/{instrutor_id}", response_model=InstrutorOut)
def obter_instrutor(instrutor_id: int, db: Session = Depends(get_db)) -> InstrutorOut:
    return _instrutor_out(_obter_ou_404(db, Instrutor, instrutor_id, "Instrutor"))


def _aplicar_dados_instrutor(db: Session, instrutor: Instrutor, dados: InstrutorIn) -> None:
    _obter_ou_404(db, Projeto, dados.projeto_id, "Projeto")
    for tipologia_id in dados.tipologia_ids:
        _obter_ou_404(db, Tipologia, tipologia_id, "Tipologia")

    instrutor.nome = dados.nome
    instrutor.projeto_id = dados.projeto_id
    instrutor.observacao = dados.observacao
    instrutor.ativo = dados.ativo
    instrutor.turnos = [
        InstrutorTurno(turno=t.turno, carga_horaria_horas=t.carga_horaria_horas)
        for t in dados.turnos
    ]
    instrutor.dias = [InstrutorDia(dia_semana=d) for d in dados.dias_semana]
    instrutor.tipologias = [InstrutorTipologia(tipologia_id=t) for t in dados.tipologia_ids]


@router.post("/instrutores", response_model=InstrutorOut, status_code=status.HTTP_201_CREATED)
def criar_instrutor(dados: InstrutorIn, db: Session = Depends(get_db)) -> InstrutorOut:
    if db.scalar(select(Instrutor).where(Instrutor.nome == dados.nome)):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Já existe um instrutor com o nome '{dados.nome}'",
        )
    instrutor = Instrutor(nome=dados.nome, projeto_id=dados.projeto_id)
    db.add(instrutor)
    _aplicar_dados_instrutor(db, instrutor, dados)
    db.commit()
    return _instrutor_out(instrutor)


@router.put("/instrutores/{instrutor_id}", response_model=InstrutorOut)
def atualizar_instrutor(
    instrutor_id: int, dados: InstrutorIn, db: Session = Depends(get_db)
) -> InstrutorOut:
    instrutor = _obter_ou_404(db, Instrutor, instrutor_id, "Instrutor")
    existente = db.scalar(select(Instrutor).where(Instrutor.nome == dados.nome))
    if existente and existente.id != instrutor_id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Já existe um instrutor com o nome '{dados.nome}'",
        )
    # `delete-orphan` remove os vínculos antigos ao substituir as coleções.
    instrutor.turnos.clear()
    instrutor.dias.clear()
    instrutor.tipologias.clear()
    db.flush()
    _aplicar_dados_instrutor(db, instrutor, dados)
    db.commit()
    return _instrutor_out(instrutor)


@router.delete("/instrutores/{instrutor_id}", status_code=status.HTTP_204_NO_CONTENT)
def remover_instrutor(instrutor_id: int, db: Session = Depends(get_db)) -> None:
    instrutor = _obter_ou_404(db, Instrutor, instrutor_id, "Instrutor")
    db.delete(instrutor)
    db.commit()


# --------------------------------------------------------------------------
# Turmas em andamento
# --------------------------------------------------------------------------


def _turma_out(turma: TurmaEmAndamento) -> TurmaEmAndamentoOut:
    return TurmaEmAndamentoOut(
        id=turma.id,
        codigo_turma=turma.codigo_turma,
        instrutor_id=turma.instrutor_id,
        instrutor_nome=turma.instrutor.nome,
        tipologia_id=turma.tipologia_id,
        tipologia_nome=turma.tipologia.nome,
        projeto_id=turma.projeto_id,
        modalidade=turma.modalidade,
        turno=turma.turno,
        data_inicio=turma.data_inicio,
        data_fim_prevista=turma.data_fim_prevista,
    )


@router.get(
    "/turmas-em-andamento",
    response_model=list[TurmaEmAndamentoOut],
    summary="Lista as turmas em execução",
    description=(
        "Ordenadas pela data de término prevista, evidenciando quais instrutores "
        "liberam capacidade primeiro."
    ),
)
def listar_turmas_andamento(db: Session = Depends(get_db)) -> list[TurmaEmAndamentoOut]:
    turmas = db.scalars(
        select(TurmaEmAndamento).order_by(TurmaEmAndamento.data_fim_prevista)
    ).all()
    return [_turma_out(t) for t in turmas]


@router.post(
    "/turmas-em-andamento",
    response_model=TurmaEmAndamentoOut,
    status_code=status.HTTP_201_CREATED,
)
def criar_turma_andamento(
    dados: TurmaEmAndamentoIn, db: Session = Depends(get_db)
) -> TurmaEmAndamentoOut:
    instrutor = _obter_ou_404(db, Instrutor, dados.instrutor_id, "Instrutor")
    _obter_ou_404(db, Tipologia, dados.tipologia_id, "Tipologia")

    disponiveis = {t.turno for t in instrutor.turnos}
    if dados.turno not in disponiveis:
        nomes = ", ".join(sorted(t.value for t in disponiveis)) or "(nenhum)"
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=(
                f"Instrutor '{instrutor.nome}' não está disponível no turno "
                f"'{dados.turno.value}'. Turnos disponíveis: {nomes}"
            ),
        )

    turma = TurmaEmAndamento(
        **dados.model_dump(),
        projeto_id=instrutor.projeto_id,
    )
    db.add(turma)
    db.commit()
    return _turma_out(turma)


@router.delete("/turmas-em-andamento/{turma_id}", status_code=status.HTTP_204_NO_CONTENT)
def remover_turma_andamento(turma_id: int, db: Session = Depends(get_db)) -> None:
    turma = _obter_ou_404(db, TurmaEmAndamento, turma_id, "Turma em andamento")
    db.delete(turma)
    db.commit()

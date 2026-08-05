"""CRUD de cenários de simulação.

Um cenário é a **configuração**; uma simulação é uma **execução** daquela
configuração (ver `app.api.simulacoes`). Os metadados ficam em SQLite; os
pesos do objetivo ficam em arquivo JSON, referenciado por
`parametros_json_path`.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import Cenario, CenarioProjeto, Projeto
from app.schemas.cenarios import CenarioIn, CenarioOut, PesosObjetivoOut
from app.services.cenarios.parametros import (
    EscopoJson,
    ParametrosCenario,
    PeriodoJson,
    PesosObjetivoJson,
    SolverConfigJson,
    atualizar_parametros,
    carregar_parametros,
    remover_parametros,
    salvar_parametros,
)

router = APIRouter(prefix="/cenarios", tags=["cenários"])


def _obter_ou_404(db: Session, cenario_id: int) -> Cenario:
    cenario = db.get(Cenario, cenario_id)
    if cenario is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Cenário {cenario_id} não encontrado"
        )
    return cenario


def _validar_projetos(db: Session, projeto_ids: list[int]) -> list[str]:
    """Confirma que os projetos existem e devolve seus nomes (para o JSON)."""
    nomes = []
    for pid in projeto_ids:
        projeto = db.get(Projeto, pid)
        if projeto is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"Projeto {pid} não encontrado"
            )
        nomes.append(projeto.nome)
    return nomes


def _montar_parametros(
    cenario_id: int | str, dados: CenarioIn, nomes_projetos: list[str]
) -> ParametrosCenario:
    return ParametrosCenario(
        cenario_id=str(cenario_id),
        descricao=dados.descricao,
        periodo=PeriodoJson(de=dados.periodo_de, ate=dados.periodo_ate),
        escopo=EscopoJson(
            projetos=nomes_projetos,
            permitir_compartilhamento_entre_projetos=dados.permitir_compartilhamento,
        ),
        pesos_objetivo=PesosObjetivoJson(**dados.pesos_objetivo.model_dump()),
        solver=SolverConfigJson(**dados.solver.model_dump()),
    )


def _cenario_out(cenario: Cenario) -> CenarioOut:
    parametros = carregar_parametros(cenario.parametros_json_path)
    return CenarioOut(
        id=cenario.id,
        nome=cenario.nome,
        descricao=cenario.descricao,
        periodo_de=cenario.periodo_de,
        periodo_ate=cenario.periodo_ate,
        projeto_ids=[cp.projeto_id for cp in cenario.projetos],
        permitir_compartilhamento=cenario.permitir_compartilhamento,
        pesos_objetivo=PesosObjetivoOut(**parametros.pesos_objetivo.model_dump()),
        criado_em=cenario.criado_em,
    )


@router.get("", response_model=list[CenarioOut])
def listar_cenarios(db: Session = Depends(get_db)) -> list[CenarioOut]:
    cenarios = db.scalars(select(Cenario).order_by(Cenario.criado_em.desc())).all()
    return [_cenario_out(c) for c in cenarios]


@router.get("/{cenario_id}", response_model=CenarioOut)
def obter_cenario(cenario_id: int, db: Session = Depends(get_db)) -> CenarioOut:
    return _cenario_out(_obter_ou_404(db, cenario_id))


@router.post("", response_model=CenarioOut, status_code=status.HTTP_201_CREATED)
def criar_cenario(dados: CenarioIn, db: Session = Depends(get_db)) -> CenarioOut:
    nomes_projetos = _validar_projetos(db, dados.projeto_ids)

    cenario = Cenario(
        nome=dados.nome,
        descricao=dados.descricao,
        periodo_de=dados.periodo_de,
        periodo_ate=dados.periodo_ate,
        permitir_compartilhamento=dados.permitir_compartilhamento,
        parametros_json_path="",  # preenchido abaixo, após termos o ID
    )
    db.add(cenario)
    db.flush()

    parametros = _montar_parametros(cenario.id, dados, nomes_projetos)
    cenario.parametros_json_path = salvar_parametros(parametros)
    cenario.projetos = [CenarioProjeto(projeto_id=pid) for pid in dados.projeto_ids]

    db.commit()
    return _cenario_out(cenario)


@router.put("/{cenario_id}", response_model=CenarioOut)
def atualizar_cenario(
    cenario_id: int, dados: CenarioIn, db: Session = Depends(get_db)
) -> CenarioOut:
    """Atualiza um cenário existente.

    O arquivo de parâmetros nunca é sobrescrito em disco — uma versão nova é
    gravada e o ponteiro do cenário passa a apontar para ela. Simulações já
    executadas guardam o caminho do arquivo vigente no momento em que
    rodaram, então continuam reportando os parâmetros que de fato usaram.
    """
    cenario = _obter_ou_404(db, cenario_id)
    nomes_projetos = _validar_projetos(db, dados.projeto_ids)

    cenario.nome = dados.nome
    cenario.descricao = dados.descricao
    cenario.periodo_de = dados.periodo_de
    cenario.periodo_ate = dados.periodo_ate
    cenario.permitir_compartilhamento = dados.permitir_compartilhamento

    parametros = _montar_parametros(cenario.id, dados, nomes_projetos)
    cenario.parametros_json_path = atualizar_parametros(parametros)

    cenario.projetos.clear()
    db.flush()
    cenario.projetos = [CenarioProjeto(projeto_id=pid) for pid in dados.projeto_ids]

    db.commit()
    return _cenario_out(cenario)


@router.post(
    "/{cenario_id}/duplicar",
    response_model=CenarioOut,
    status_code=status.HTTP_201_CREATED,
    summary="Duplica um cenário para variar apenas o que se deseja comparar",
)
def duplicar_cenario(cenario_id: int, db: Session = Depends(get_db)) -> CenarioOut:
    original = _obter_ou_404(db, cenario_id)
    parametros_originais = carregar_parametros(original.parametros_json_path)

    copia = Cenario(
        nome=f"{original.nome} (cópia)",
        descricao=original.descricao,
        periodo_de=original.periodo_de,
        periodo_ate=original.periodo_ate,
        permitir_compartilhamento=original.permitir_compartilhamento,
        parametros_json_path="",
    )
    db.add(copia)
    db.flush()

    novos_parametros = parametros_originais.model_copy(update={"cenario_id": str(copia.id)})
    copia.parametros_json_path = salvar_parametros(novos_parametros)
    copia.projetos = [
        CenarioProjeto(projeto_id=cp.projeto_id) for cp in original.projetos
    ]

    db.commit()
    return _cenario_out(copia)


@router.delete("/{cenario_id}", status_code=status.HTTP_204_NO_CONTENT)
def remover_cenario(cenario_id: int, db: Session = Depends(get_db)) -> None:
    cenario = _obter_ou_404(db, cenario_id)
    caminho_atual = cenario.parametros_json_path
    db.delete(cenario)
    db.commit()
    remover_parametros(caminho_atual)

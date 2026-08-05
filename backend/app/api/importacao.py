"""Rotas de importação de planilhas e download dos modelos."""

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.importacao import ResultadoImportacaoOut
from app.services.importacao.modelos import (
    ModeloDesconhecidoError,
    gerar_modelo,
    tipos_disponiveis,
)
from app.services.importacao.parser_instrutores import importar_instrutores
from app.services.importacao.parser_tipologias import importar_tipologias
from app.services.importacao.parser_turmas_andamento import importar_turmas_andamento

router = APIRouter(prefix="/importar", tags=["importação"])

TIPO_XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


async def _ler_upload(arquivo: UploadFile) -> tuple[bytes, str]:
    conteudo = await arquivo.read()
    if not conteudo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="O arquivo enviado está vazio."
        )
    return conteudo, arquivo.filename or "planilha.xlsx"


@router.post(
    "/instrutores",
    response_model=ResultadoImportacaoOut,
    summary="Importa a planilha de instrutores",
    description=(
        "Cria ou atualiza instrutores com seus turnos, dias e tipologias. "
        "As tipologias e os projetos encontrados são criados automaticamente — "
        "as tipologias nascem pendentes de configuração de carga horária. "
        "Reimportar atualiza os instrutores existentes em vez de duplicá-los."
    ),
)
async def importar_instrutores_endpoint(
    arquivo: UploadFile = File(description="Planilha .xlsx ou .csv"),
    db: Session = Depends(get_db),
) -> ResultadoImportacaoOut:
    conteudo, nome = await _ler_upload(arquivo)
    return ResultadoImportacaoOut.de_resultado(importar_instrutores(db, conteudo, nome))


@router.post(
    "/tipologias",
    response_model=ResultadoImportacaoOut,
    summary="Configura a carga horária das tipologias",
    description=(
        "Completa a carga horária total e as horas por encontro das tipologias "
        "derivadas da planilha de instrutores. A carga total precisa ser múltiplo "
        "exato das horas por encontro."
    ),
)
async def importar_tipologias_endpoint(
    arquivo: UploadFile = File(description="Planilha .xlsx ou .csv"),
    db: Session = Depends(get_db),
) -> ResultadoImportacaoOut:
    conteudo, nome = await _ler_upload(arquivo)
    return ResultadoImportacaoOut.de_resultado(importar_tipologias(db, conteudo, nome))


@router.post(
    "/turmas-em-andamento",
    response_model=ResultadoImportacaoOut,
    summary="Importa a situação atual das alocações",
    description=(
        "Registra as turmas em execução, que consomem capacidade dos instrutores "
        "até sua data de término. Planilha sem linhas é cenário válido: significa "
        "que nenhuma turma está em curso."
    ),
)
async def importar_turmas_endpoint(
    arquivo: UploadFile = File(description="Planilha .xlsx ou .csv"),
    db: Session = Depends(get_db),
) -> ResultadoImportacaoOut:
    conteudo, nome = await _ler_upload(arquivo)
    return ResultadoImportacaoOut.de_resultado(importar_turmas_andamento(db, conteudo, nome))


@router.get(
    "/modelos/{tipo}",
    summary="Baixa uma planilha-modelo",
    description=(
        "Retorna a planilha em branco com os cabeçalhos corretos, linhas de "
        "exemplo e uma aba com orientações de preenchimento."
    ),
    response_class=Response,
)
def baixar_modelo(tipo: str) -> Response:
    try:
        conteudo, nome_arquivo = gerar_modelo(tipo)
    except ModeloDesconhecidoError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return Response(
        content=conteudo,
        media_type=TIPO_XLSX,
        headers={"Content-Disposition": f'attachment; filename="{nome_arquivo}"'},
    )


@router.get(
    "/modelos",
    summary="Lista os modelos disponíveis",
)
def listar_modelos() -> dict[str, list[str]]:
    return {"tipos": tipos_disponiveis()}

"""Importação da planilha de datas não letivas.

Feriados, recessos e férias — persistidos na v1, mas **sem efeito** sobre a
geração de calendários. O gerador de encontros ainda não os consulta; a
funcionalidade fica pronta para ser ativada numa versão futura, quando a
regra de deslocamento de encontros for definida.
"""

from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import DataNaoLetiva, Projeto
from app.models.enums import TipoDataNaoLetiva
from app.services.importacao.campos import ValorInvalidoError, parse_data
from app.services.importacao.leitor_planilha import Linha, ler_planilha, normalizar_cabecalho
from app.services.importacao.resultado import ArquivoInvalidoError, ResultadoImportacao
from app.services.importacao.transacao import Resultado, processar_linhas

COLUNAS_OBRIGATORIAS = ["data_inicio", "descricao"]

AVISO_SEM_EFEITO_CALCULO = (
    "Os dados foram importados, mas ainda não afetam o cálculo das simulações "
    "— a funcionalidade está reservada para uma versão futura."
)

# Sextas-feiras e fins de semana já não recebem turma regular — um registro
# cobrindo só esses dias é aceito, mas sinalizado como sem efeito prático.
DIAS_ISO_SEM_EFEITO = {5, 6, 7}  # sexta, sábado, domingo


def importar_datas_nao_letivas(
    db: Session, conteudo: bytes, nome_arquivo: str
) -> ResultadoImportacao:
    resultado = ResultadoImportacao()

    try:
        planilha = ler_planilha(conteudo, nome_arquivo)
        planilha.exigir_colunas(COLUNAS_OBRIGATORIAS)
    except ArquivoInvalidoError as exc:
        resultado.erro_arquivo = str(exc)
        return resultado

    registros_processados: list[DataNaoLetiva] = []

    def processar(sessao: Session, linha: Linha) -> str:
        registro = _importar_linha(sessao, linha)
        registros_processados.append(registro)
        return Resultado.CRIADO

    processar_linhas(db, planilha.linhas, processar, resultado)

    for registro in registros_processados:
        _alertar_sem_efeito_pratico(registro, resultado)

    resultado.adicionar_alerta(AVISO_SEM_EFEITO_CALCULO)
    return resultado


def _importar_linha(db: Session, linha: Linha) -> DataNaoLetiva:
    data_inicio = parse_data(linha.texto("data_inicio"), "Data de início")

    texto_fim = linha.texto("data_fim")
    data_fim = parse_data(texto_fim, "Data de término") if texto_fim else data_inicio
    if data_fim < data_inicio:
        raise ValorInvalidoError(
            f"Data de término ({data_fim:%d/%m/%Y}) é anterior à de início ({data_inicio:%d/%m/%Y})"
        )

    descricao = linha.texto("descricao")
    if not descricao:
        raise ValorInvalidoError("Descrição não informada")

    tipo = _parse_tipo(linha.texto("tipo"))
    projeto_id = _resolver_projeto(db, linha.texto("projeto"))

    registro = DataNaoLetiva(
        data_inicio=data_inicio,
        data_fim=data_fim,
        descricao=descricao,
        tipo=tipo,
        projeto_id=projeto_id,
    )
    db.add(registro)
    db.flush()
    return registro


def _parse_tipo(texto: str) -> TipoDataNaoLetiva:
    if not texto:
        return TipoDataNaoLetiva.FERIADO
    try:
        return TipoDataNaoLetiva(normalizar_cabecalho(texto))
    except ValueError:
        validos = ", ".join(t.value for t in TipoDataNaoLetiva)
        raise ValorInvalidoError(f"Tipo inválido: '{texto}'. Valores aceitos: {validos}") from None


def _resolver_projeto(db: Session, nome: str) -> int | None:
    if not nome:
        return None  # vazio significa "todos os projetos"
    projeto = db.scalar(select(Projeto).where(Projeto.nome == nome))
    if projeto is None:
        raise ValorInvalidoError(f"Projeto não encontrado: '{nome}'")
    return projeto.id


def _alertar_sem_efeito_pratico(registro: DataNaoLetiva, resultado: ResultadoImportacao) -> None:
    """Sinaliza intervalo que cobre só sexta/sábado/domingo — dias que já não têm aula."""
    if _cobre_apenas_dias_sem_efeito(registro.data_inicio, registro.data_fim):
        resultado.adicionar_alerta(
            f"'{registro.descricao}' cobre apenas sextas-feiras e/ou fim de semana — "
            "sem efeito prático, já que esses dias não recebem turma regular."
        )


def _cobre_apenas_dias_sem_efeito(data_inicio: date, data_fim: date) -> bool:
    data_atual = data_inicio
    while data_atual <= data_fim:
        if data_atual.isoweekday() not in DIAS_ISO_SEM_EFEITO:
            return False
        data_atual += timedelta(days=1)
    return True

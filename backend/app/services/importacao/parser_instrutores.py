"""Importação da planilha de instrutores.

Esta é a entrada principal do sistema. Além de criar os instrutores, **deriva o
catálogo de tipologias e a lista de projetos** — uma tipologia só é ofertável
porque algum instrutor a domina, então o catálogo nasce daqui e não de um
cadastro prévio.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import (
    Instrutor,
    InstrutorDia,
    InstrutorTipologia,
    InstrutorTurno,
    Projeto,
    Tipologia,
)
from app.services.importacao.campos import (
    ValorInvalidoError,
    parse_dias_semana,
    parse_lista,
    parse_turnos,
)
from app.services.importacao.leitor_planilha import Linha, ler_planilha
from app.services.importacao.resultado import ArquivoInvalidoError, ResultadoImportacao
from app.services.importacao.transacao import Resultado, processar_linhas

COLUNAS_OBRIGATORIAS = ["nome", "projeto", "turnos", "dias_semana", "tipologias"]


def importar_instrutores(
    db: Session, conteudo: bytes, nome_arquivo: str
) -> ResultadoImportacao:
    """Importa a planilha de instrutores, atualizando os já existentes.

    A planilha é a fonte de verdade da disponibilidade: reimportar substitui
    turnos, dias e tipologias do instrutor em vez de duplicá-lo.
    """
    resultado = ResultadoImportacao()

    try:
        planilha = ler_planilha(conteudo, nome_arquivo)
        planilha.exigir_colunas(COLUNAS_OBRIGATORIAS)
    except ArquivoInvalidoError as exc:
        resultado.erro_arquivo = str(exc)
        return resultado

    processar_linhas(db, planilha.linhas, _importar_linha, resultado)

    _alertar_tipologias_pendentes(db, resultado)
    return resultado


def _importar_linha(db: Session, linha: Linha) -> str:
    nome = linha.texto("nome")
    if not nome:
        raise ValorInvalidoError("Nome do instrutor não informado")

    nome_projeto = linha.texto("projeto")
    if not nome_projeto:
        raise ValorInvalidoError("Projeto não informado")

    turnos = parse_turnos(linha.texto("turnos"))
    dias = parse_dias_semana(linha.texto("dias_semana"))

    nomes_tipologias = parse_lista(linha.texto("tipologias"))
    if not nomes_tipologias:
        # Um instrutor sem tipologia não gera nenhuma oferta possível.
        raise ValorInvalidoError("Instrutor sem nenhuma tipologia")

    projeto = _obter_ou_criar_projeto(db, nome_projeto)
    tipologias = [_obter_ou_criar_tipologia(db, n) for n in nomes_tipologias]

    existente = db.scalar(select(Instrutor).where(Instrutor.nome == nome))
    if existente is None:
        instrutor = Instrutor(nome=nome, projeto_id=projeto.id)
        db.add(instrutor)
        situacao = Resultado.CRIADO
    else:
        instrutor = existente
        instrutor.projeto_id = projeto.id
        # `delete-orphan` remove os vínculos antigos ao substituir as coleções.
        instrutor.turnos.clear()
        instrutor.dias.clear()
        instrutor.tipologias.clear()
        db.flush()
        situacao = Resultado.ATUALIZADO

    instrutor.observacao = linha.texto("observacao") or None
    instrutor.turnos = [InstrutorTurno(turno=turno) for turno in turnos]
    instrutor.dias = [InstrutorDia(dia_semana=dia) for dia in dias]
    instrutor.tipologias = [InstrutorTipologia(tipologia_id=t.id) for t in tipologias]

    db.flush()
    return situacao


def _obter_ou_criar_projeto(db: Session, nome: str) -> Projeto:
    projeto = db.scalar(select(Projeto).where(Projeto.nome == nome))
    if projeto is None:
        projeto = Projeto(nome=nome)
        db.add(projeto)
        db.flush()
    return projeto


def _obter_ou_criar_tipologia(db: Session, nome: str) -> Tipologia:
    """Cria a tipologia se inédita, sem carga horária.

    Ela nasce pendente de configuração e bloqueia a simulação até que a carga
    horária seja informada — a lacuna fica visível cedo, em vez de deixar a
    simulação rodar com dados incompletos.
    """
    tipologia = db.scalar(select(Tipologia).where(Tipologia.nome == nome))
    if tipologia is None:
        tipologia = Tipologia(nome=nome)
        db.add(tipologia)
        db.flush()
    return tipologia


def _alertar_tipologias_pendentes(db: Session, resultado: ResultadoImportacao) -> None:
    pendentes = [
        t.nome
        for t in db.scalars(select(Tipologia)).all()
        if not t.configurada
    ]
    if pendentes:
        resultado.adicionar_alerta(
            f"{len(pendentes)} tipologia(s) pendente(s) de configuração de carga horária: "
            + ", ".join(sorted(pendentes))
            + ". A simulação fica bloqueada até que sejam configuradas."
        )

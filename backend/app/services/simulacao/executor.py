"""Execução de uma simulação: carrega dados, resolve o modelo, persiste o resultado.

Roda em segundo plano — o disparo (`POST /simulacoes/executar`) retorna
imediatamente, sem bloquear o cliente. Usa sua própria sessão de banco: a
sessão da requisição original já foi encerrada quando esta tarefa executa.
"""

import json
import logging
import time
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models import (
    OportunidadeSimulacao,
    ResultadoKpis,
    Simulacao,
    SnapshotCapacidade,
    StatusSimulacao,
    TurmaSugerida,
    TurmaSugeridaEncontro,
)
from app.services.cenarios.parametros import ArquivoParametrosError, carregar_parametros
from app.services.simulacao.repositorio import (
    carregar_instrutores,
    carregar_tipologias_configuradas,
    carregar_turmas_andamento,
)
from app.services.solver.cp_sat_model import ConfiguracaoSolver, PesosObjetivo, resolver
from app.services.solver.gerador_candidatas import gerar_candidatas
from app.services.solver.metricas import ResultadoMetricas, calcular_metricas

logger = logging.getLogger(__name__)


def executar_simulacao(simulacao_id: int) -> None:
    """Ponto de entrada da tarefa de background."""
    db = SessionLocal()
    try:
        _executar(db, simulacao_id)
    except Exception as exc:  # noqa: BLE001 - qualquer falha vira status de erro, não crash silencioso
        logger.exception("Falha ao executar simulação %s", simulacao_id)
        _marcar_erro(db, simulacao_id, str(exc))
    finally:
        db.close()


def _executar(db: Session, simulacao_id: int) -> None:
    simulacao = db.get(Simulacao, simulacao_id)
    if simulacao is None:
        logger.error("Simulação %s não encontrada ao iniciar execução", simulacao_id)
        return

    simulacao.status = StatusSimulacao.EXECUTANDO
    db.commit()

    try:
        parametros = carregar_parametros(simulacao.parametros_json_path)
    except ArquivoParametrosError as exc:
        _marcar_erro(db, simulacao_id, str(exc))
        return

    cenario = simulacao.cenario
    escopo_ids = [cp.projeto_id for cp in cenario.projetos]
    permitir_compartilhamento = cenario.permitir_compartilhamento

    instrutores = carregar_instrutores(
        db, None if (permitir_compartilhamento or not escopo_ids) else escopo_ids
    )
    tipologias = carregar_tipologias_configuradas(db)
    instrutor_ids = {i.id for i in instrutores}
    turmas_andamento = carregar_turmas_andamento(db, instrutor_ids)

    t0 = time.perf_counter()
    candidatas = gerar_candidatas(
        instrutores=instrutores,
        tipologias=tipologias,
        turmas_andamento=turmas_andamento,
        periodo_de=cenario.periodo_de,
        periodo_ate=cenario.periodo_ate,
        projetos_escopo=frozenset(escopo_ids),
        permitir_compartilhamento=permitir_compartilhamento,
    )
    logger.info(
        "Simulação %s: %d candidatas geradas em %.2fs",
        simulacao_id,
        len(candidatas),
        time.perf_counter() - t0,
    )

    resultado = resolver(
        candidatas=candidatas,
        instrutores=instrutores,
        tipologias=tipologias,
        turmas_andamento=turmas_andamento,
        periodo_de=cenario.periodo_de,
        periodo_ate=cenario.periodo_ate,
        pesos=PesosObjetivo(**parametros.pesos_objetivo.model_dump()),
        configuracao=ConfiguracaoSolver(**parametros.solver.model_dump()),
    )

    metricas = calcular_metricas(
        resultado_solver=resultado,
        candidatas_geradas=candidatas,
        instrutores=instrutores,
        turmas_andamento=turmas_andamento,
        periodo_de=cenario.periodo_de,
        periodo_ate=cenario.periodo_ate,
    )

    _persistir_resultado(db, simulacao, resultado.candidatas_selecionadas, metricas)

    simulacao.status = StatusSimulacao.CONCLUIDA
    simulacao.concluido_em = datetime.now(UTC)
    simulacao.tempo_execucao_seg = resultado.tempo_execucao_seg
    simulacao.solver_status = resultado.status
    simulacao.objetivo_valor = resultado.objetivo_valor
    db.commit()


def _persistir_resultado(
    db: Session, simulacao: Simulacao, candidatas_selecionadas, metricas: ResultadoMetricas
) -> None:
    """Grava turmas sugeridas, encontros, KPIs e snapshot de capacidade.

    Resultado vazio (nenhuma turma viável) é conclusão normal: os KPIs e o
    snapshot ainda são gravados, só não há linhas em `turmas_sugeridas`.
    """
    for candidata in candidatas_selecionadas:
        turma = TurmaSugerida(
            simulacao_id=simulacao.id,
            tipologia_id=candidata.tipologia_id,
            instrutor_id=candidata.instrutor_id,
            projeto_id=candidata.projeto_id,
            modalidade=candidata.modalidade,
            turno=candidata.turno,
            semana_inicio=candidata.semana_inicio,
            data_inicio=candidata.calendario.data_inicio,
            data_fim=candidata.calendario.data_fim,
            num_encontros=candidata.calendario.num_encontros,
            carga_horaria_total=candidata.calendario.carga_horaria_total,
        )
        db.add(turma)
        db.flush()  # garante turma.id para os encontros abaixo

        db.add_all(
            TurmaSugeridaEncontro(
                turma_sugerida_id=turma.id,
                data=encontro.data,
                turno=encontro.turno,
                horas=encontro.horas,
            )
            for encontro in candidata.calendario.encontros
        )

    slots_disponiveis_total = sum(u.slots_disponiveis for u in metricas.utilizacao_por_instrutor)
    db.add(
        ResultadoKpis(
            simulacao_id=simulacao.id,
            total_turmas_sugeridas=metricas.metadados.total_turmas_sugeridas,
            horas_formacao_total=metricas.metadados.horas_formacao_total,
            slots_disponiveis_total=slots_disponiveis_total,
            pct_ociosidade=metricas.pct_ociosidade,
            indice_balanceamento_carga=metricas.indice_balanceamento_carga,
            indice_balanceamento_tipologia=metricas.indice_balanceamento_tipologias,
            slots_reposicao_sexta=metricas.slots_reposicao_sexta,
        )
    )

    db.add_all(
        SnapshotCapacidade(
            simulacao_id=simulacao.id,
            instrutor_id=u.instrutor_id,
            slots_disponiveis=u.slots_disponiveis,
            slots_ocupados=u.slots_alocados,
            primeira_data_livre=metricas.primeira_data_livre.get(u.instrutor_id),
            primeira_data_livre_por_slot_json=json.dumps(
                {
                    turno.value: data.isoformat()
                    for turno, data in metricas.primeira_data_livre_por_slot.get(
                        u.instrutor_id, {}
                    ).items()
                }
            ),
        )
        for u in metricas.utilizacao_por_instrutor
    )

    # Agregado de TODAS as candidatas geradas (não só as selecionadas) — é o
    # que permite ao mapa de oportunidades responder "o que poderia ser
    # aberto e quando", já que a decisão final é da equipe, não do solver.
    db.add_all(
        OportunidadeSimulacao(
            simulacao_id=simulacao.id,
            tipologia_id=o.tipologia_id,
            data_inicio=o.data_inicio,
            total_turmas=o.total_turmas,
            instrutor_ids_csv=",".join(str(i) for i in o.instrutor_ids),
        )
        for o in metricas.oportunidades
    )


def _marcar_erro(db: Session, simulacao_id: int, mensagem: str) -> None:
    try:
        simulacao = db.get(Simulacao, simulacao_id)
        if simulacao is not None:
            simulacao.status = StatusSimulacao.ERRO
            simulacao.mensagem_erro = mensagem
            simulacao.concluido_em = datetime.now(UTC)
            db.commit()
    except Exception:  # noqa: BLE001 - último recurso; não deixar a tarefa quebrar em silêncio
        logger.exception("Falha ao registrar erro da simulação %s", simulacao_id)

import { useState } from "react";
import { useSearchParams } from "react-router-dom";
import { api } from "../../api/cliente";
import { ApiError } from "../../api/erros";
import type { Simulacao } from "../../api/types";
import { Alert } from "../../components/Alert";
import { Button } from "../../components/Button";
import { Spinner } from "../../components/Spinner";
import { Tabs } from "../../components/Tabs";
import { useAcompanharSimulacao } from "../../hooks/useAcompanharSimulacao";
import { MapaOportunidades } from "./resultado/MapaOportunidades";
import { PainelIndicadores } from "./resultado/PainelIndicadores";
import { SeletorSimulacao } from "./SeletorSimulacao";
import styles from "./OportunidadesPage.module.css";

const ABAS = [
  { id: "mapa", rotulo: "Mapa de Oportunidades" },
  { id: "indicadores", rotulo: "Indicadores" },
];

/** Tela central: a partir de quando cada tipologia pode ser aberta, e com quais instrutores. */
export function OportunidadesPage() {
  const [params, setParams] = useSearchParams();
  const simulacaoIdParam = params.get("simulacao");
  const simulacaoId = simulacaoIdParam ? Number(simulacaoIdParam) : null;
  const abaParam = params.get("aba");
  const abaAtiva = abaParam === "indicadores" ? "indicadores" : "mapa";

  const { simulacao, erro } = useAcompanharSimulacao(simulacaoId);
  const [reexecutando, setReexecutando] = useState(false);
  const [erroReexecucao, setErroReexecucao] = useState<string | null>(null);

  function selecionarSimulacao(id: number): void {
    setParams({ simulacao: String(id) });
  }

  function selecionarAba(id: string): void {
    setParams((atual) => {
      const novo = new URLSearchParams(atual);
      novo.set("aba", id);
      return novo;
    });
  }

  async function reexecutar(): Promise<void> {
    if (!simulacao) return;
    setReexecutando(true);
    setErroReexecucao(null);
    try {
      const nova = await api.post<Simulacao>("/simulacoes/executar", {
        cenario_id: simulacao.cenario_id,
      });
      setParams({ simulacao: String(nova.id) });
    } catch (excecao) {
      setErroReexecucao(
        excecao instanceof ApiError ? excecao.message : "Não foi possível executar novamente.",
      );
    } finally {
      setReexecutando(false);
    }
  }

  return (
    <div className={styles.container}>
      <h1 className={styles.titulo}>Mapa de Oportunidades</h1>

      {simulacaoId === null && <SeletorSimulacao onSelecionar={selecionarSimulacao} />}

      {simulacaoId !== null && erro && <Alert variante="erro">{erro.message}</Alert>}

      {simulacaoId !== null && !erro && !simulacao && <Spinner rotulo="Carregando simulação…" />}

      {simulacao && (simulacao.status === "pendente" || simulacao.status === "executando") && (
        <Alert variante="info" titulo="Simulação em execução">
          <div className={styles.andamento}>
            <Spinner rotulo="Processando…" />
            <span>
              {Math.max(
                0,
                Math.round((Date.now() - Date.parse(simulacao.iniciado_em)) / 1000),
              )}
              s decorridos — a página atualiza automaticamente ao concluir.
            </span>
          </div>
        </Alert>
      )}

      {simulacao && simulacao.status === "erro" && (
        <Alert variante="erro" titulo="A simulação terminou em erro">
          <div className={styles.andamento}>
            <span>{simulacao.mensagem_erro ?? "Erro não especificado."}</span>
            <Button onClick={reexecutar} carregando={reexecutando}>
              Executar novamente
            </Button>
          </div>
          {erroReexecucao && <p>{erroReexecucao}</p>}
        </Alert>
      )}

      {simulacao && simulacao.status === "concluida" && (
        <>
          {simulacao.solver_status === "OTIMO" && (
            <Alert variante="sucesso" titulo="Solução ótima encontrada">
              O solver encontrou e comprovou a melhor solução possível para este cenário.
            </Alert>
          )}
          {simulacao.solver_status === "FACTIVEL" && (
            <Alert variante="alerta" titulo="Busca interrompida por tempo">
              O limite de tempo foi atingido. O resultado abaixo é viável, mas pode não ser o
              ótimo.
            </Alert>
          )}

          <Tabs abas={ABAS} abaAtiva={abaAtiva} onSelecionar={selecionarAba} />

          {abaAtiva === "mapa" ? (
            <MapaOportunidades simulacaoId={simulacao.id} />
          ) : (
            <PainelIndicadores simulacaoId={simulacao.id} simulacao={simulacao} />
          )}
        </>
      )}
    </div>
  );
}

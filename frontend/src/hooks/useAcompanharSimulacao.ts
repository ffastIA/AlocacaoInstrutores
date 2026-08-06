import { useEffect, useState } from "react";
import { api } from "../api/cliente";
import type { Simulacao } from "../api/types";

const INTERVALO_CONSULTA_MS = 2000;

const STATUS_EM_ANDAMENTO: Simulacao["status"][] = ["pendente", "executando"];

/**
 * Acompanha uma simulação em execução por consulta periódica, encerrando
 * automaticamente ao concluir ou falhar — sem exigir que a tela gerencie o
 * temporizador.
 */
export function useAcompanharSimulacao(simulacaoId: number | null): {
  simulacao: Simulacao | null;
  erro: Error | null;
} {
  const [simulacao, setSimulacao] = useState<Simulacao | null>(null);
  const [erro, setErro] = useState<Error | null>(null);

  useEffect(() => {
    setSimulacao(null);
    setErro(null);

    if (simulacaoId === null) {
      return;
    }

    let cancelado = false;
    let temporizador: ReturnType<typeof setTimeout> | undefined;

    async function consultar(): Promise<void> {
      try {
        const resultado = await api.get<Simulacao>(`/simulacoes/${simulacaoId}`);
        if (cancelado) return;

        setSimulacao(resultado);
        if (STATUS_EM_ANDAMENTO.includes(resultado.status)) {
          temporizador = setTimeout(consultar, INTERVALO_CONSULTA_MS);
        }
      } catch (excecao) {
        if (!cancelado) setErro(excecao as Error);
      }
    }

    void consultar();

    return () => {
      cancelado = true;
      if (temporizador !== undefined) clearTimeout(temporizador);
    };
  }, [simulacaoId]);

  return { simulacao, erro };
}

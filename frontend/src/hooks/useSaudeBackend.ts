import { useCallback, useEffect, useState } from "react";
import { api } from "../api/cliente";

type EstadoSaude = "verificando" | "disponivel" | "indisponivel";

/** Verifica se o backend está acessível, com opção de tentar novamente. */
export function useSaudeBackend(): { estado: EstadoSaude; tentarNovamente: () => void } {
  const [estado, setEstado] = useState<EstadoSaude>("verificando");
  const [tentativa, setTentativa] = useState(0);

  const tentarNovamente = useCallback(() => setTentativa((n) => n + 1), []);

  useEffect(() => {
    let cancelado = false;
    setEstado("verificando");

    api
      .get("/health")
      .then(() => {
        if (!cancelado) setEstado("disponivel");
      })
      .catch(() => {
        // Qualquer falha (rede fora do ar, timeout, resposta inesperada)
        // significa que a API não está utilizável no momento.
        if (!cancelado) setEstado("indisponivel");
      });

    return () => {
      cancelado = true;
    };
  }, [tentativa]);

  return { estado, tentarNovamente };
}

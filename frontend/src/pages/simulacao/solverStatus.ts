import type { Tom } from "../../components/tons";

/** Metadados do status do solver — reaproveitados no card de Metadados e no
 * Alert de topo do Mapa de Oportunidades, para que o tom e o rótulo nunca divirjam. */
export const SOLVER_STATUS_META: Record<string, { rotulo: string; tom: Tom; descricao: string }> = {
  OTIMO: {
    rotulo: "Ótimo",
    tom: "sucesso",
    descricao: "A melhor solução possível foi encontrada e comprovada.",
  },
  FACTIVEL: {
    rotulo: "Factível",
    tom: "alerta",
    descricao:
      "A busca foi interrompida por tempo — o resultado é viável, mas pode não ser o ótimo.",
  },
  INVIAVEL: {
    rotulo: "Inviável",
    tom: "erro",
    descricao: "Nenhuma solução viável foi encontrada para os parâmetros informados.",
  },
};

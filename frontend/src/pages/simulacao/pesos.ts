import type { PesosObjetivo } from "../../api/types";

/** Metadados dos quatro pesos do objetivo — reaproveitados no formulário de
 * cenário e no painel de indicadores, para que a explicação seja sempre a mesma. */
export const PESOS_META: { chave: keyof PesosObjetivo; rotulo: string; descricao: string }[] = [
  {
    chave: "maximizar_aproveitamento",
    rotulo: "Aproveitamento",
    descricao: "Prioriza usar o máximo de horas disponíveis dos instrutores.",
  },
  {
    chave: "antecipar_inicio",
    rotulo: "Antecipação",
    descricao: "Prioriza abrir turmas o quanto antes dentro do período simulado.",
  },
  {
    chave: "balancear_carga_instrutores",
    rotulo: "Equilíbrio de carga",
    descricao: "Evita concentrar turmas em poucos instrutores, distribuindo a ocupação.",
  },
  {
    chave: "balancear_tipologias",
    rotulo: "Equilíbrio de tipologias",
    descricao: "Evita que instrutores multi-tipologia concentrem a oferta em uma só.",
  },
];

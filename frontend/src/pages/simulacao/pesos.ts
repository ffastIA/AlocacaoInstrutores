import type { PesosObjetivo } from "../../api/types";
import type { Tom } from "../../components/tons";

/** Metadados dos quatro pesos do objetivo — reaproveitados no formulário de
 * cenário e no painel de indicadores, para que a explicação seja sempre a mesma.
 * `cor` é fixa por peso e nunca muda entre telas, para que a barra de pesos
 * seja lida da mesma forma em qualquer lugar em que apareça. */
export const PESOS_META: { chave: keyof PesosObjetivo; rotulo: string; descricao: string; cor: Tom }[] =
  [
    {
      chave: "maximizar_aproveitamento",
      rotulo: "Aproveitamento",
      descricao: "Prioriza usar o máximo de horas disponíveis dos instrutores.",
      cor: "primaria",
    },
    {
      chave: "antecipar_inicio",
      rotulo: "Antecipação",
      descricao: "Prioriza abrir turmas o quanto antes dentro do período simulado.",
      cor: "sucesso",
    },
    {
      chave: "balancear_carga_instrutores",
      rotulo: "Equilíbrio de carga",
      descricao: "Evita concentrar turmas em poucos instrutores, distribuindo a ocupação.",
      cor: "info",
    },
    {
      chave: "balancear_tipologias",
      rotulo: "Equilíbrio de tipologias",
      descricao: "Evita que instrutores multi-tipologia concentrem a oferta em uma só.",
      cor: "alerta",
    },
  ];

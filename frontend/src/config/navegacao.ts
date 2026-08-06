/**
 * Fonte única das rotas da aplicação — usada tanto pelo roteador (`App.tsx`)
 * quanto pela navegação lateral (`Sidebar.tsx`), para que as duas nunca
 * fiquem dessincronizadas.
 */

export interface ItemNavegacao {
  rotulo: string;
  caminho: string;
}

export interface GrupoNavegacao {
  titulo: string;
  itens: ItemNavegacao[];
}

export const GRUPOS_NAVEGACAO: GrupoNavegacao[] = [
  {
    titulo: "Dados",
    itens: [
      { rotulo: "Importação", caminho: "/dados/importacao" },
      { rotulo: "Cadastros", caminho: "/dados/cadastros" },
      { rotulo: "Situação Atual", caminho: "/dados/situacao-atual" },
      { rotulo: "Datas Não Letivas", caminho: "/dados/datas-nao-letivas" },
    ],
  },
  {
    titulo: "Simulação",
    itens: [
      { rotulo: "Cenários", caminho: "/simulacao/cenarios" },
      { rotulo: "Mapa de Oportunidades", caminho: "/simulacao/oportunidades" },
      { rotulo: "Agenda por Instrutor", caminho: "/simulacao/agenda" },
      { rotulo: "Comparação", caminho: "/simulacao/comparacao" },
      { rotulo: "Histórico", caminho: "/simulacao/historico" },
    ],
  },
];

export const CAMINHO_INICIAL = "/dados/importacao";

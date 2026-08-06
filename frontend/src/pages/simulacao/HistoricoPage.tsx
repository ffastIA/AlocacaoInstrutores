import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../../api/cliente";
import { ApiError } from "../../api/erros";
import type { Cenario, Kpis, Simulacao } from "../../api/types";
import { Alert } from "../../components/Alert";
import { EmptyState } from "../../components/EmptyState";
import { Select } from "../../components/Select";
import { Spinner } from "../../components/Spinner";
import { Table } from "../../components/Table";
import type { ColunaTabela } from "../../components/Table";
import styles from "./HistoricoPage.module.css";

const ROTULO_STATUS: Record<string, string> = {
  pendente: "Pendente",
  executando: "Executando",
  concluida: "Concluída",
  erro: "Falha",
};

/** Histórico de simulações executadas, com acesso ao resultado de cada uma. */
export function HistoricoPage() {
  const navegar = useNavigate();
  const [simulacoes, setSimulacoes] = useState<Simulacao[] | null>(null);
  const [cenarios, setCenarios] = useState<Cenario[]>([]);
  const [kpisPorSimulacao, setKpisPorSimulacao] = useState<Map<number, Kpis>>(new Map());
  const [filtroCenario, setFiltroCenario] = useState("");
  const [erro, setErro] = useState<string | null>(null);

  async function carregar(): Promise<void> {
    try {
      const query = filtroCenario ? `?cenario_id=${filtroCenario}` : "";
      const [listaSimulacoes, listaCenarios] = await Promise.all([
        api.get<Simulacao[]>(`/simulacoes${query}`),
        api.get<Cenario[]>("/cenarios"),
      ]);
      setSimulacoes(listaSimulacoes);
      setCenarios(listaCenarios);

      const concluidas = listaSimulacoes.filter((s) => s.status === "concluida");
      const pares = await Promise.all(
        concluidas.map(async (s) => {
          try {
            return [s.id, await api.get<Kpis>(`/simulacoes/${s.id}/kpis`)] as const;
          } catch {
            return null;
          }
        }),
      );
      setKpisPorSimulacao(
        new Map(pares.filter((p): p is [number, Kpis] => p !== null)),
      );
    } catch (excecao) {
      setErro(excecao instanceof ApiError ? excecao.message : "Falha ao carregar o histórico.");
    }
  }

  useEffect(() => {
    void carregar();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filtroCenario]);

  if (erro) return <Alert variante="erro">{erro}</Alert>;
  if (simulacoes === null) return <Spinner rotulo="Carregando histórico…" />;

  const colunas: ColunaTabela<Simulacao>[] = [
    {
      chave: "id",
      titulo: "Simulação",
      renderizar: (s) =>
        s.status === "concluida" ? (
          <button
            type="button"
            className={styles.linkNome}
            onClick={() => navegar(`/simulacao/oportunidades?simulacao=${s.id}`)}
          >
            #{s.id}
          </button>
        ) : (
          `#${s.id}`
        ),
    },
    {
      chave: "cenario",
      titulo: "Cenário",
      renderizar: (s) => cenarios.find((c) => c.id === s.cenario_id)?.nome ?? `#${s.cenario_id}`,
    },
    {
      chave: "iniciado_em",
      titulo: "Executada em",
      ordenavel: true,
      valorOrdenacao: (s) => s.iniciado_em,
      renderizar: (s) => s.iniciado_em.slice(0, 16).replace("T", " "),
    },
    {
      chave: "status",
      titulo: "Status",
      renderizar: (s) => (
        <span className={s.status === "erro" ? styles.marcaFalha : undefined}>
          {ROTULO_STATUS[s.status]}
          {s.status === "erro" && s.mensagem_erro && (
            <span className={styles.mensagemErro}> — {s.mensagem_erro}</span>
          )}
        </span>
      ),
    },
    {
      chave: "indicadores",
      titulo: "Indicadores principais",
      renderizar: (s) => {
        const kpis = kpisPorSimulacao.get(s.id);
        if (!kpis) return "—";
        return `${kpis.total_turmas_sugeridas} turma(s) · ${kpis.pct_ociosidade.toFixed(1)}% ociosidade`;
      },
    },
  ];

  return (
    <div className={styles.container}>
      <div className={styles.cabecalho}>
        <h1 className={styles.titulo}>Histórico de Simulações</h1>
        <Select
          rotulo="Filtrar por cenário"
          opcoes={[
            { valor: "", rotulo: "Todos" },
            ...cenarios.map((c) => ({ valor: String(c.id), rotulo: c.nome })),
          ]}
          value={filtroCenario}
          onChange={(e) => setFiltroCenario(e.target.value)}
        />
      </div>

      {simulacoes.length === 0 ? (
        <EmptyState
          titulo="Nenhuma simulação executada"
          descricao="Crie um cenário e execute-o para ver o histórico aqui."
        />
      ) : (
        <Table colunas={colunas} linhas={simulacoes} chaveLinha={(s) => s.id} />
      )}
    </div>
  );
}

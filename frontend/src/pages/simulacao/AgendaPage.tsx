import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { api } from "../../api/cliente";
import { ApiError } from "../../api/erros";
import type { AgendaItem, CapacidadeInstrutor, Projeto } from "../../api/types";
import { Alert } from "../../components/Alert";
import { BarraProporcional } from "../../components/BarraProporcional";
import { EmptyState } from "../../components/EmptyState";
import { Select } from "../../components/Select";
import { Selo } from "../../components/Selo";
import { Spinner } from "../../components/Spinner";
import { Table } from "../../components/Table";
import type { ColunaTabela } from "../../components/Table";
import { useAcompanharSimulacao } from "../../hooks/useAcompanharSimulacao";
import { formatarData } from "../../utils/data";
import { SeletorSimulacao } from "./SeletorSimulacao";
import styles from "./AgendaPage.module.css";

const ROTULO_TURNO: Record<string, string> = {
  manha_1: "Manhã 1",
  manha_2: "Manhã 2",
  tarde_1: "Tarde 1",
  tarde_2: "Tarde 2",
  noite: "Noite",
};
const ROTULO_MODALIDADE: Record<string, string> = {
  regular_seg_qua: "Regular (seg/qua)",
  regular_ter_qui: "Regular (ter/qui)",
  intensiva_seg_qui: "Intensiva (seg a qui)",
};

/** Ocupação por instrutor: visão consolidada e agenda individual de uma simulação. */
export function AgendaPage() {
  const [params, setParams] = useSearchParams();
  const simulacaoIdParam = params.get("simulacao");
  const simulacaoId = simulacaoIdParam ? Number(simulacaoIdParam) : null;

  const { simulacao, erro: erroSimulacao } = useAcompanharSimulacao(simulacaoId);

  const [capacidade, setCapacidade] = useState<CapacidadeInstrutor[] | null>(null);
  const [projetos, setProjetos] = useState<Projeto[]>([]);
  const [filtroProjeto, setFiltroProjeto] = useState("");
  const [erro, setErro] = useState<string | null>(null);

  const [instrutorSelecionado, setInstrutorSelecionado] = useState<number | null>(null);
  const [agenda, setAgenda] = useState<AgendaItem[] | null>(null);

  function selecionarSimulacao(id: number): void {
    setParams({ simulacao: String(id) });
  }

  useEffect(() => {
    if (!simulacao || simulacao.status !== "concluida") return;
    const params2 = new URLSearchParams();
    if (filtroProjeto) params2.set("projeto_id", filtroProjeto);
    const query = params2.toString();
    Promise.all([
      api.get<CapacidadeInstrutor[]>(
        `/simulacoes/${simulacao.id}/capacidade-instrutores${query ? `?${query}` : ""}`,
      ),
      api.get<Projeto[]>("/projetos"),
    ])
      .then(([lista, listaProjetos]) => {
        setCapacidade(lista);
        setProjetos(listaProjetos);
      })
      .catch((excecao) => {
        setErro(excecao instanceof ApiError ? excecao.message : "Falha ao carregar a agenda.");
      });
  }, [simulacao, filtroProjeto]);

  useEffect(() => {
    if (!simulacao || instrutorSelecionado === null) {
      setAgenda(null);
      return;
    }
    api
      .get<AgendaItem[]>(`/simulacoes/${simulacao.id}/agenda/${instrutorSelecionado}`)
      .then(setAgenda)
      .catch((excecao) => {
        setErro(excecao instanceof ApiError ? excecao.message : "Falha ao carregar a agenda.");
      });
  }, [simulacao, instrutorSelecionado]);

  const colunas: ColunaTabela<CapacidadeInstrutor>[] = [
    {
      chave: "instrutor",
      titulo: "Instrutor",
      renderizar: (c) => (
        <button
          type="button"
          className={styles.linkNome}
          onClick={() => setInstrutorSelecionado(c.instrutor_id)}
        >
          {c.instrutor_nome}
        </button>
      ),
    },
    { chave: "projeto", titulo: "Projeto", renderizar: (c) => c.projeto_nome },
    { chave: "disponiveis", titulo: "Slots disponíveis", numerica: true, renderizar: (c) => c.slots_disponiveis },
    { chave: "ocupados", titulo: "Slots ocupados", numerica: true, renderizar: (c) => c.slots_ocupados },
    {
      chave: "utilizacao",
      titulo: "Utilização",
      numerica: true,
      ordenavel: true,
      valorOrdenacao: (c) => c.utilizacao_percentual,
      renderizar: (c) => (
        <div className={styles.celulaUtilizacao}>
          <BarraProporcional
            tamanho="compacta"
            papel="medidor"
            maximo={100}
            rotulo="Utilização"
            segmentos={[{ rotulo: "Utilização", valor: c.utilizacao_percentual, cor: "primaria" }]}
          />
          <span>{c.utilizacao_percentual}%</span>
        </div>
      ),
    },
    {
      chave: "primeira_data_livre",
      titulo: "Primeira data livre",
      ordenavel: true,
      valorOrdenacao: (c) => c.primeira_data_livre ?? "",
      renderizar: (c) => (c.primeira_data_livre ? formatarData(c.primeira_data_livre) : "Já disponível"),
    },
  ];

  const instrutorAtual = capacidade?.find((c) => c.instrutor_id === instrutorSelecionado) ?? null;

  return (
    <div className={styles.container}>
      <h1 className={styles.titulo}>Agenda por Instrutor</h1>

      {simulacaoId === null && <SeletorSimulacao onSelecionar={selecionarSimulacao} />}
      {simulacaoId !== null && erroSimulacao && (
        <Alert variante="erro">{erroSimulacao.message}</Alert>
      )}
      {simulacaoId !== null && !erroSimulacao && !simulacao && (
        <Spinner rotulo="Carregando simulação…" />
      )}
      {simulacao && simulacao.status !== "concluida" && (
        <Alert variante="info">Aguardando a conclusão da simulação selecionada.</Alert>
      )}
      {erro && <Alert variante="erro">{erro}</Alert>}

      {simulacao && simulacao.status === "concluida" && (
        <>
          {instrutorSelecionado === null ? (
            <>
              <div className={styles.filtros}>
                <Select
                  rotulo="Projeto"
                  opcoes={[
                    { valor: "", rotulo: "Todos" },
                    ...projetos.map((p) => ({ valor: String(p.id), rotulo: p.nome })),
                  ]}
                  value={filtroProjeto}
                  onChange={(e) => setFiltroProjeto(e.target.value)}
                />
              </div>
              {capacidade === null ? (
                <Spinner rotulo="Carregando instrutores…" />
              ) : capacidade.length === 0 ? (
                <EmptyState titulo="Nenhum instrutor no escopo desta simulação" />
              ) : (
                <Table colunas={colunas} linhas={capacidade} chaveLinha={(c) => c.instrutor_id} />
              )}
            </>
          ) : (
            <div className={styles.agendaIndividual}>
              <button
                type="button"
                className={styles.linkVoltar}
                onClick={() => setInstrutorSelecionado(null)}
              >
                ← Voltar à visão consolidada
              </button>

              <h2 className={styles.subtitulo}>{instrutorAtual?.instrutor_nome}</h2>
              {instrutorAtual && (
                <div className={styles.resumoUtilizacao}>
                  <BarraProporcional
                    papel="medidor"
                    maximo={100}
                    rotulo="Utilização"
                    segmentos={[
                      {
                        rotulo: "Utilização",
                        valor: instrutorAtual.utilizacao_percentual,
                        cor: "primaria",
                      },
                    ]}
                  />
                  <p className={styles.resumo}>
                    {instrutorAtual.utilizacao_percentual}% de utilização ·{" "}
                    {instrutorAtual.slots_ocupados} de {instrutorAtual.slots_disponiveis} slots
                    ocupados ·{" "}
                    {instrutorAtual.primeira_data_livre
                      ? `livre a partir de ${formatarData(instrutorAtual.primeira_data_livre)}`
                      : "já disponível"}
                  </p>
                </div>
              )}

              {agenda === null ? (
                <Spinner rotulo="Carregando agenda…" />
              ) : agenda.length === 0 ? (
                <EmptyState
                  titulo="Instrutor integralmente disponível"
                  descricao="Nenhuma turma em andamento ou sugerida nesta simulação."
                />
              ) : (
                <ul className={styles.listaAgenda}>
                  {agenda.map((item, indice) => (
                    <li key={indice} className={styles.itemAgenda}>
                      <Selo tom={item.origem === "em_andamento" ? "info" : "primaria"}>
                        {item.origem === "em_andamento" ? "Em andamento" : "Sugerida"}
                      </Selo>
                      <span>
                        {item.tipologia_nome} — {ROTULO_MODALIDADE[item.modalidade]} —{" "}
                        {ROTULO_TURNO[item.turno]} — {formatarData(item.data_inicio)} a{" "}
                        {formatarData(item.data_fim)}
                      </span>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          )}
        </>
      )}
    </div>
  );
}

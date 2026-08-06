import { useEffect, useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { api } from "../../../api/cliente";
import { ApiError } from "../../../api/erros";
import type {
  Instrutor,
  Oportunidade,
  Projeto,
  Tipologia,
  TurmaSugerida,
} from "../../../api/types";
import { Alert } from "../../../components/Alert";
import { Button } from "../../../components/Button";
import { Card } from "../../../components/Card";
import { DateRangeField } from "../../../components/DateRangeField";
import { EmptyState } from "../../../components/EmptyState";
import { Modal } from "../../../components/Modal";
import { Select } from "../../../components/Select";
import { Selo } from "../../../components/Selo";
import { Spinner } from "../../../components/Spinner";
import { Tabs } from "../../../components/Tabs";
import { formatarData } from "../../../utils/data";
import { LinhaDoTempoOportunidades } from "./LinhaDoTempoOportunidades";
import styles from "./MapaOportunidades.module.css";

const VISUALIZACOES = [
  { id: "tabela", rotulo: "Tabela" },
  { id: "linha-do-tempo", rotulo: "Linha do tempo" },
];

interface MapaOportunidadesProps {
  simulacaoId: number;
}

const ROTULO_TURNO: Record<string, string> = {
  manha_1: "Manhã 1",
  manha_2: "Manhã 2",
  tarde_1: "Tarde 1",
  tarde_2: "Tarde 2",
  noite: "Noite",
};

export function MapaOportunidades({ simulacaoId }: MapaOportunidadesProps) {
  const [params, setParams] = useSearchParams();
  const visualizacao = params.get("visualizacao") === "linha-do-tempo" ? "linha-do-tempo" : "tabela";

  function selecionarVisualizacao(id: string): void {
    setParams((atual) => {
      const novo = new URLSearchParams(atual);
      novo.set("visualizacao", id);
      return novo;
    });
  }

  const [oportunidades, setOportunidades] = useState<Oportunidade[] | null>(null);
  const [turmasSugeridas, setTurmasSugeridas] = useState<TurmaSugerida[]>([]);
  const [instrutores, setInstrutores] = useState<Instrutor[]>([]);
  const [tipologias, setTipologias] = useState<Tipologia[]>([]);
  const [projetos, setProjetos] = useState<Projeto[]>([]);
  const [erro, setErro] = useState<string | null>(null);
  const [exportando, setExportando] = useState(false);
  const [erroExportar, setErroExportar] = useState<string | null>(null);

  const [filtroTipologia, setFiltroTipologia] = useState("");
  const [filtroInstrutor, setFiltroInstrutor] = useState("");
  const [filtroProjeto, setFiltroProjeto] = useState("");
  const [filtroDe, setFiltroDe] = useState("");
  const [filtroAte, setFiltroAte] = useState("");

  const [detalhe, setDetalhe] = useState<{ tipologiaNome: string; dataInicio: string } | null>(
    null,
  );

  async function carregarBase(): Promise<void> {
    try {
      const [listaTurmas, listaInstrutores, listaTipologias, listaProjetos] = await Promise.all([
        api.get<TurmaSugerida[]>(`/simulacoes/${simulacaoId}/turmas-sugeridas`),
        api.get<Instrutor[]>("/instrutores"),
        api.get<Tipologia[]>("/tipologias"),
        api.get<Projeto[]>("/projetos"),
      ]);
      setTurmasSugeridas(listaTurmas);
      setInstrutores(listaInstrutores);
      setTipologias(listaTipologias);
      setProjetos(listaProjetos);
    } catch (excecao) {
      setErro(excecao instanceof ApiError ? excecao.message : "Falha ao carregar o resultado.");
    }
  }

  async function carregarOportunidades(): Promise<void> {
    try {
      const params = new URLSearchParams();
      if (filtroTipologia) params.set("tipologia_id", filtroTipologia);
      if (filtroInstrutor) params.set("instrutor_id", filtroInstrutor);
      if (filtroDe) params.set("data_de", filtroDe);
      if (filtroAte) params.set("data_ate", filtroAte);
      const query = params.toString();
      const lista = await api.get<Oportunidade[]>(
        `/simulacoes/${simulacaoId}/oportunidades${query ? `?${query}` : ""}`,
      );
      setOportunidades(lista);
    } catch (excecao) {
      setErro(excecao instanceof ApiError ? excecao.message : "Falha ao carregar oportunidades.");
    }
  }

  useEffect(() => {
    void carregarBase();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [simulacaoId]);

  useEffect(() => {
    void carregarOportunidades();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [simulacaoId, filtroTipologia, filtroInstrutor, filtroDe, filtroAte]);

  const instrutorPorId = useMemo(() => new Map(instrutores.map((i) => [i.id, i])), [instrutores]);

  const oportunidadesFiltradas = useMemo(() => {
    if (!oportunidades) return null;
    if (!filtroProjeto) return oportunidades;
    return oportunidades.filter((o) =>
      o.instrutor_ids.some((id) => instrutorPorId.get(id)?.projeto_id === Number(filtroProjeto)),
    );
  }, [oportunidades, filtroProjeto, instrutorPorId]);

  // Datas em que o mesmo instrutor aparece em mais de uma tipologia — sinal de
  // que ali existe uma escolha entre alternativas, não turmas cumulativas.
  const chavesAlternativa = useMemo(() => {
    if (!oportunidadesFiltradas) return new Set<string>();
    const porInstrutorData = new Map<string, Set<number>>();
    for (const o of oportunidadesFiltradas) {
      for (const instrutorId of o.instrutor_ids) {
        const chave = `${instrutorId}::${o.data_inicio}`;
        const tipologias = porInstrutorData.get(chave) ?? new Set<number>();
        tipologias.add(o.tipologia_id);
        porInstrutorData.set(chave, tipologias);
      }
    }
    const resultado = new Set<string>();
    for (const [chave, tips] of porInstrutorData) {
      if (tips.size > 1) resultado.add(chave);
    }
    return resultado;
  }, [oportunidadesFiltradas]);

  const grupos = useMemo(() => {
    if (!oportunidadesFiltradas) return [];
    const porTipologia = new Map<string, Oportunidade[]>();
    for (const o of oportunidadesFiltradas) {
      const lista = porTipologia.get(o.tipologia_nome) ?? [];
      lista.push(o);
      porTipologia.set(o.tipologia_nome, lista);
    }
    return [...porTipologia.entries()]
      .map(([tipologiaNome, itens]) => ({
        tipologiaNome,
        itens: itens.sort((a, b) => a.data_inicio.localeCompare(b.data_inicio)),
      }))
      .sort((a, b) => a.tipologiaNome.localeCompare(b.tipologiaNome));
  }, [oportunidadesFiltradas]);

  async function exportar(): Promise<void> {
    setExportando(true);
    setErroExportar(null);
    try {
      const { blob, nomeArquivo } = await api.baixarArquivo(`/simulacoes/${simulacaoId}/exportar`);
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = nomeArquivo ?? `simulacao_${simulacaoId}.xlsx`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(url);
    } catch (excecao) {
      setErroExportar(
        excecao instanceof ApiError ? excecao.message : "Não foi possível exportar o resultado.",
      );
    } finally {
      setExportando(false);
    }
  }

  const turmasDoDetalhe = detalhe
    ? turmasSugeridas.filter(
        (t) => t.tipologia_nome === detalhe.tipologiaNome && t.data_inicio === detalhe.dataInicio,
      )
    : [];

  if (erro) return <Alert variante="erro">{erro}</Alert>;
  if (oportunidadesFiltradas === null) return <Spinner rotulo="Carregando oportunidades…" />;

  return (
    <div className={styles.container}>
      <div className={styles.barraSuperior}>
        <div className={styles.filtros}>
          <Select
            rotulo="Tipologia"
            opcoes={[
              { valor: "", rotulo: "Todas" },
              ...tipologias.map((t) => ({ valor: String(t.id), rotulo: t.nome })),
            ]}
            value={filtroTipologia}
            onChange={(e) => setFiltroTipologia(e.target.value)}
          />
          <Select
            rotulo="Instrutor"
            opcoes={[
              { valor: "", rotulo: "Todos" },
              ...instrutores.map((i) => ({ valor: String(i.id), rotulo: i.nome })),
            ]}
            value={filtroInstrutor}
            onChange={(e) => setFiltroInstrutor(e.target.value)}
          />
          <Select
            rotulo="Projeto"
            opcoes={[
              { valor: "", rotulo: "Todos" },
              ...projetos.map((p) => ({ valor: String(p.id), rotulo: p.nome })),
            ]}
            value={filtroProjeto}
            onChange={(e) => setFiltroProjeto(e.target.value)}
          />
          <DateRangeField
            rotuloInicio="Início — de"
            rotuloFim="Início — até"
            valorInicio={filtroDe}
            valorFim={filtroAte}
            onChangeInicio={setFiltroDe}
            onChangeFim={setFiltroAte}
          />
        </div>
        <Button variante="secundaria" onClick={exportar} carregando={exportando}>
          Exportar resultado
        </Button>
      </div>

      {erroExportar && <Alert variante="erro">{erroExportar}</Alert>}

      {grupos.length === 0 ? (
        <EmptyState
          titulo="Nenhuma oportunidade encontrada"
          descricao={
            turmasSugeridas.length === 0 && !filtroTipologia && !filtroInstrutor && !filtroProjeto
              ? "Não há oportunidade de abertura de turma no período simulado com os dados atuais."
              : "Nenhuma oportunidade corresponde aos filtros aplicados."
          }
        />
      ) : (
        <>
          <Tabs abas={VISUALIZACOES} abaAtiva={visualizacao} onSelecionar={selecionarVisualizacao} />

          {visualizacao === "linha-do-tempo" ? (
            <LinhaDoTempoOportunidades
              grupos={grupos}
              chavesAlternativa={chavesAlternativa}
              onSelecionarDetalhe={(tipologiaNome, dataInicio) =>
                setDetalhe({ tipologiaNome, dataInicio })
              }
            />
          ) : (
            <div className={styles.grupos}>
              {grupos.map((grupo) => (
                <Card key={grupo.tipologiaNome} titulo={grupo.tipologiaNome}>
                  <div className={styles.tabelaScroll}>
                    <table className={styles.tabela}>
                      <thead>
                        <tr>
                          <th>Data de início</th>
                          <th>Turmas possíveis</th>
                          <th>Instrutores</th>
                        </tr>
                      </thead>
                      <tbody>
                        {grupo.itens.map((o) => (
                          <tr key={`${o.tipologia_id}-${o.data_inicio}`}>
                            <td>{formatarData(o.data_inicio)}</td>
                            <td>
                              <button
                                type="button"
                                className={styles.linkDetalhe}
                                onClick={() =>
                                  setDetalhe({
                                    tipologiaNome: grupo.tipologiaNome,
                                    dataInicio: o.data_inicio,
                                  })
                                }
                              >
                                {o.total_turmas}
                              </button>
                            </td>
                            <td>
                              {o.instrutor_ids.map((id, indice) => {
                                const nome = instrutorPorId.get(id)?.nome ?? `#${id}`;
                                const alternativa = chavesAlternativa.has(
                                  `${id}::${o.data_inicio}`,
                                );
                                return (
                                  <span key={id}>
                                    {indice > 0 && ", "}
                                    {nome}
                                    {alternativa && (
                                      <>
                                        {" "}
                                        <Selo tom="alerta">alternativa entre tipologias</Selo>
                                      </>
                                    )}
                                  </span>
                                );
                              })}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </Card>
              ))}
            </div>
          )}
        </>
      )}

      <Modal
        aberto={detalhe !== null}
        titulo={detalhe ? `${detalhe.tipologiaNome} — ${formatarData(detalhe.dataInicio)}` : ""}
        onFechar={() => setDetalhe(null)}
      >
        {turmasDoDetalhe.length === 0 ? (
          <p className={styles.semSelecao}>
            Esta oportunidade não foi selecionada pelo otimizador nesta execução — outra
            alternativa foi escolhida para essa data.
          </p>
        ) : (
          <div className={styles.listaDetalhe}>
            {turmasDoDetalhe.map((turma) => (
              <div key={turma.id} className={styles.itemDetalhe}>
                <p>
                  <strong>{turma.instrutor_nome}</strong> — {ROTULO_TURNO[turma.turno]}
                </p>
                <p>Modalidade: {turma.modalidade}</p>
                <p>
                  {formatarData(turma.data_inicio)} a {formatarData(turma.data_fim)} ·{" "}
                  {turma.num_encontros} encontro(s) ·{" "}
                  {turma.carga_horaria_total}h
                </p>
              </div>
            ))}
          </div>
        )}
      </Modal>
    </div>
  );
}

import { useEffect, useMemo, useState } from "react";
import { api } from "../../api/cliente";
import { ApiError } from "../../api/erros";
import type { Cenario, Comparacao, ComparacaoItem, Simulacao } from "../../api/types";
import { Alert } from "../../components/Alert";
import { EmptyState } from "../../components/EmptyState";
import { Spinner } from "../../components/Spinner";
import { PESOS_META } from "./pesos";
import styles from "./ComparacaoPage.module.css";

interface Linha {
  rotulo: string;
  valor: (item: ComparacaoItem) => string;
}

function criarLinhas(cenarios: Cenario[]): Linha[] {
  return [
    { rotulo: "Cenário", valor: (i) => i.cenario_nome },
    { rotulo: "Período", valor: (i) => `${i.periodo_de} a ${i.periodo_ate}` },
    {
      rotulo: "Escopo",
      valor: (i) => {
        const projetoIds = cenarios.find((c) => c.id === i.cenario_id)?.projeto_ids ?? [];
        return projetoIds.length === 0 ? "Todos os projetos" : `${projetoIds.length} projeto(s)`;
      },
    },
    {
      rotulo: "Compartilhamento entre projetos",
      valor: (i) => (i.permitir_compartilhamento ? "Sim" : "Não"),
    },
    ...PESOS_META.map((meta) => ({
      rotulo: `Peso — ${meta.rotulo}`,
      valor: (i: ComparacaoItem) => String(i.pesos_objetivo[meta.chave]),
    })),
    { rotulo: "Total de turmas sugeridas", valor: (i) => String(i.kpis.total_turmas_sugeridas) },
    { rotulo: "Horas de formação", valor: (i) => `${i.kpis.horas_formacao_total}h` },
    { rotulo: "Ociosidade", valor: (i) => `${i.kpis.pct_ociosidade.toFixed(1)}%` },
    {
      rotulo: "Equilíbrio de carga",
      valor: (i) => i.kpis.indice_balanceamento_carga.toFixed(1),
    },
    {
      rotulo: "Equilíbrio de tipologias",
      valor: (i) => i.kpis.indice_balanceamento_tipologia.toFixed(1),
    },
    { rotulo: "Slots de reposição às sextas", valor: (i) => String(i.kpis.slots_reposicao_sexta) },
  ];
}

/** Compara os indicadores de duas ou mais simulações concluídas lado a lado. */
export function ComparacaoPage() {
  const [simulacoes, setSimulacoes] = useState<Simulacao[] | null>(null);
  const [cenarios, setCenarios] = useState<Cenario[]>([]);
  const [selecionadas, setSelecionadas] = useState<number[]>([]);
  const [comparacao, setComparacao] = useState<Comparacao | null>(null);
  const [erro, setErro] = useState<string | null>(null);
  const [carregando, setCarregando] = useState(false);

  useEffect(() => {
    Promise.all([api.get<Simulacao[]>("/simulacoes"), api.get<Cenario[]>("/cenarios")])
      .then(([listaSimulacoes, listaCenarios]) => {
        setSimulacoes(listaSimulacoes);
        setCenarios(listaCenarios);
      })
      .catch((excecao) => {
        setErro(excecao instanceof ApiError ? excecao.message : "Falha ao carregar simulações.");
      });
  }, []);

  function alternarSelecao(id: number, concluida: boolean): void {
    if (!concluida) return;
    setSelecionadas((atual) =>
      atual.includes(id) ? atual.filter((s) => s !== id) : [...atual, id],
    );
  }

  useEffect(() => {
    if (selecionadas.length < 2) {
      setComparacao(null);
      return;
    }
    setCarregando(true);
    setErro(null);
    api
      .get<Comparacao>(`/simulacoes/comparar?ids=${selecionadas.join(",")}`)
      .then(setComparacao)
      .catch((excecao) => {
        setErro(excecao instanceof ApiError ? excecao.message : "Falha ao comparar simulações.");
      })
      .finally(() => setCarregando(false));
  }, [selecionadas]);

  const linhas = useMemo(() => criarLinhas(cenarios), [cenarios]);

  const linhasComDiferenca = useMemo(() => {
    if (!comparacao) return new Set<number>();
    const resultado = new Set<number>();
    linhas.forEach((linha, indice) => {
      const valores = comparacao.itens.map((item) => linha.valor(item));
      if (new Set(valores).size > 1) resultado.add(indice);
    });
    return resultado;
  }, [comparacao, linhas]);

  if (erro) return <Alert variante="erro">{erro}</Alert>;
  if (simulacoes === null) return <Spinner rotulo="Carregando simulações…" />;

  return (
    <div className={styles.container}>
      <h1 className={styles.titulo}>Comparação de Cenários</h1>

      {simulacoes.length === 0 ? (
        <EmptyState
          titulo="Nenhuma simulação para comparar"
          descricao="Execute ao menos duas simulações para poder compará-las."
        />
      ) : (
        <>
          <div className={styles.selecao}>
            <p className={styles.instrucao}>
              Selecione duas ou mais simulações concluídas para comparar:
            </p>
            <ul className={styles.listaSelecao}>
              {simulacoes.map((s) => {
                const concluida = s.status === "concluida";
                return (
                  <li key={s.id} className={styles.itemSelecao}>
                    <label className={concluida ? undefined : styles.itemDesabilitado}>
                      <input
                        type="checkbox"
                        checked={selecionadas.includes(s.id)}
                        disabled={!concluida}
                        onChange={() => alternarSelecao(s.id, concluida)}
                      />
                      #{s.id} —{" "}
                      {cenarios.find((c) => c.id === s.cenario_id)?.nome ?? `cenário ${s.cenario_id}`}{" "}
                      ({s.iniciado_em.slice(0, 16).replace("T", " ")})
                      {!concluida && " — ainda não concluída"}
                    </label>
                  </li>
                );
              })}
            </ul>
          </div>

          {carregando && <Spinner rotulo="Comparando…" />}

          {comparacao && (
            <>
              {comparacao.periodos_divergentes && (
                <Alert variante="alerta" titulo="Períodos diferentes">
                  As simulações comparadas usam períodos diferentes — os valores absolutos não
                  são diretamente comparáveis.
                </Alert>
              )}

              <div className={styles.tabelaScroll}>
                <table className={styles.tabela}>
                  <thead>
                    <tr>
                      <th></th>
                      {comparacao.itens.map((item) => (
                        <th key={item.simulacao_id}>Simulação #{item.simulacao_id}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {linhas.map((linha, indice) => (
                      <tr key={linha.rotulo}>
                        <th className={styles.rotuloLinha}>{linha.rotulo}</th>
                        {comparacao.itens.map((item) => (
                          <td
                            key={item.simulacao_id}
                            className={linhasComDiferenca.has(indice) ? styles.diferenca : undefined}
                          >
                            {linha.valor(item)}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </>
          )}
        </>
      )}
    </div>
  );
}

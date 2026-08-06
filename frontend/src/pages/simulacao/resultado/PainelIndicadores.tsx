import { useEffect, useState } from "react";
import { api } from "../../../api/cliente";
import { ApiError } from "../../../api/erros";
import type {
  CapacidadeInstrutor,
  Cenario,
  Kpis,
  Simulacao,
  TurmaSugerida,
} from "../../../api/types";
import { Alert } from "../../../components/Alert";
import { BarraProporcional } from "../../../components/BarraProporcional";
import { Card } from "../../../components/Card";
import { Selo } from "../../../components/Selo";
import { Spinner } from "../../../components/Spinner";
import { Table } from "../../../components/Table";
import type { ColunaTabela } from "../../../components/Table";
import { formatarData, formatarDataHora } from "../../../utils/data";
import { PESOS_META } from "../pesos";
import { SOLVER_STATUS_META } from "../solverStatus";
import styles from "./PainelIndicadores.module.css";

interface PainelIndicadoresProps {
  simulacaoId: number;
  simulacao: Simulacao;
}

const EXPLICACOES: Record<string, string> = {
  pct_ociosidade:
    "Percentual da capacidade horária dos instrutores que não foi usada em nenhuma turma sugerida.",
  total_turmas_sugeridas: "Quantidade de turmas que a simulação sugere abrir no período.",
  horas_formacao_total: "Soma das horas de formação entregues pelas turmas sugeridas.",
  indice_balanceamento_carga:
    "Diferença entre o instrutor mais e o menos utilizado. Quanto menor, mais equilibrada a carga.",
  indice_balanceamento_tipologia:
    "Diferença entre a tipologia mais e a menos ofertada. Quanto menor, mais equilibrada a oferta entre tipologias.",
};

export function PainelIndicadores({ simulacaoId, simulacao }: PainelIndicadoresProps) {
  const [kpis, setKpis] = useState<Kpis | null>(null);
  const [capacidade, setCapacidade] = useState<CapacidadeInstrutor[] | null>(null);
  const [turmasSugeridas, setTurmasSugeridas] = useState<TurmaSugerida[]>([]);
  const [cenario, setCenario] = useState<Cenario | null>(null);
  const [erro, setErro] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([
      api.get<Kpis>(`/simulacoes/${simulacaoId}/kpis`),
      api.get<CapacidadeInstrutor[]>(`/simulacoes/${simulacaoId}/capacidade-instrutores`),
      api.get<TurmaSugerida[]>(`/simulacoes/${simulacaoId}/turmas-sugeridas`),
      api.get<Cenario>(`/cenarios/${simulacao.cenario_id}`),
    ])
      .then(([k, c, t, ce]) => {
        setKpis(k);
        setCapacidade(c);
        setTurmasSugeridas(t);
        setCenario(ce);
      })
      .catch((excecao) => {
        setErro(excecao instanceof ApiError ? excecao.message : "Falha ao carregar indicadores.");
      });
  }, [simulacaoId, simulacao.cenario_id]);

  if (erro) return <Alert variante="erro">{erro}</Alert>;
  if (!kpis || !capacidade || !cenario) return <Spinner rotulo="Carregando indicadores…" />;

  const distribuicaoTipologia = new Map<string, number>();
  for (const turma of turmasSugeridas) {
    distribuicaoTipologia.set(
      turma.tipologia_nome,
      (distribuicaoTipologia.get(turma.tipologia_nome) ?? 0) + 1,
    );
  }

  const colunasCapacidade: ColunaTabela<CapacidadeInstrutor>[] = [
    { chave: "instrutor", titulo: "Instrutor", renderizar: (c) => c.instrutor_nome },
    { chave: "projeto", titulo: "Projeto", renderizar: (c) => c.projeto_nome },
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
      renderizar: (c) => formatarData(c.primeira_data_livre),
    },
  ];

  return (
    <div className={styles.container}>
      <Card titulo="Metadados da execução">
        <div className={styles.grade}>
          <div>
            <p className={styles.valor}>{formatarDataHora(simulacao.iniciado_em)}</p>
            <p className={styles.rotulo}>Executada em</p>
          </div>
          <div>
            <p className={styles.valor}>
              {simulacao.tempo_execucao_seg?.toFixed(1) ?? "—"}s
            </p>
            <p className={styles.rotulo}>Tempo consumido</p>
          </div>
          <div>
            {simulacao.solver_status ? (
              <Selo tom={SOLVER_STATUS_META[simulacao.solver_status]?.tom ?? "neutro"}>
                {SOLVER_STATUS_META[simulacao.solver_status]?.rotulo ?? simulacao.solver_status}
              </Selo>
            ) : (
              <p className={styles.valor}>—</p>
            )}
            <p className={styles.rotulo}>
              {simulacao.solver_status
                ? (SOLVER_STATUS_META[simulacao.solver_status]?.descricao ?? "Qualidade da solução")
                : "Qualidade da solução"}
            </p>
          </div>
        </div>
      </Card>

      <Card titulo="Indicadores principais">
        <div className={styles.grade}>
          <div>
            <p className={styles.valor}>{kpis.pct_ociosidade.toFixed(1)}%</p>
            <p className={styles.rotulo}>Ociosidade</p>
            <p className={styles.explicacao}>{EXPLICACOES.pct_ociosidade}</p>
          </div>
          <div>
            <p className={styles.valor}>{kpis.total_turmas_sugeridas}</p>
            <p className={styles.rotulo}>Turmas sugeridas</p>
            <p className={styles.explicacao}>{EXPLICACOES.total_turmas_sugeridas}</p>
          </div>
          <div>
            <p className={styles.valor}>{kpis.horas_formacao_total}h</p>
            <p className={styles.rotulo}>Horas de formação</p>
            <p className={styles.explicacao}>{EXPLICACOES.horas_formacao_total}</p>
          </div>
          <div>
            <p className={styles.valor}>{kpis.indice_balanceamento_carga.toFixed(1)}</p>
            <p className={styles.rotulo}>Equilíbrio de carga</p>
            <p className={styles.explicacao}>{EXPLICACOES.indice_balanceamento_carga}</p>
          </div>
          <div>
            <p className={styles.valor}>{kpis.indice_balanceamento_tipologia.toFixed(1)}</p>
            <p className={styles.rotulo}>Equilíbrio de tipologias</p>
            <p className={styles.explicacao}>{EXPLICACOES.indice_balanceamento_tipologia}</p>
          </div>
          <div>
            <p className={styles.valor}>{kpis.slots_reposicao_sexta}</p>
            <p className={styles.rotulo}>Slots de reposição às sextas</p>
            <p className={styles.explicacao}>
              Sexta-feira não recebe turma regular — esses slots ficam disponíveis apenas para
              reposição.
            </p>
          </div>
        </div>
      </Card>

      <Card titulo="Pesos do objetivo desta execução">
        <BarraProporcional
          papel="distribuicao"
          segmentos={PESOS_META.map((meta) => ({
            rotulo: meta.rotulo,
            valor: cenario.pesos_objetivo[meta.chave],
            cor: meta.cor,
          }))}
        />
        <ul className={styles.listaPesos}>
          {PESOS_META.map((meta) => (
            <li key={meta.chave}>
              <strong>{meta.rotulo}:</strong> {cenario.pesos_objetivo[meta.chave]} —{" "}
              {meta.descricao}
            </li>
          ))}
        </ul>
      </Card>

      <Card titulo="Distribuição de turmas por tipologia">
        {distribuicaoTipologia.size === 0 ? (
          <p className={styles.semDados}>Nenhuma turma foi sugerida nesta simulação.</p>
        ) : (
          <div className={styles.listaDistribuicao}>
            {[...distribuicaoTipologia.entries()].map(([nome, total]) => (
              <div key={nome} className={styles.linhaDistribuicao}>
                <div className={styles.linhaDistribuicaoTexto}>
                  <span>{nome}</span>
                  <span>{total} turma(s)</span>
                </div>
                <BarraProporcional
                  tamanho="compacta"
                  papel="distribuicao"
                  maximo={Math.max(...distribuicaoTipologia.values())}
                  segmentos={[{ rotulo: nome, valor: total, cor: "primaria" }]}
                />
              </div>
            ))}
          </div>
        )}
      </Card>

      <Card titulo="Utilização por instrutor">
        {capacidade.length === 0 ? (
          <p className={styles.semDados}>Nenhum instrutor no escopo desta simulação.</p>
        ) : (
          <Table colunas={colunasCapacidade} linhas={capacidade} chaveLinha={(c) => c.instrutor_id} />
        )}
      </Card>
    </div>
  );
}

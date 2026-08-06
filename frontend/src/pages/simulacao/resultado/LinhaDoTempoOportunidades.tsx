import { useMemo } from "react";
import type { Oportunidade } from "../../../api/types";
import { formatarData } from "../../../utils/data";
import styles from "./LinhaDoTempoOportunidades.module.css";

interface GrupoOportunidades {
  tipologiaNome: string;
  itens: Oportunidade[];
}

interface LinhaDoTempoOportunidadesProps {
  grupos: GrupoOportunidades[];
  chavesAlternativa: Set<string>;
  onSelecionarDetalhe: (tipologiaNome: string, dataInicio: string) => void;
}

const DIAMETRO_MIN = 10;
const DIAMETRO_MAX = 26;

/**
 * Dot plot cronológico: uma raia por tipologia, um marcador por data
 * candidata, tamanho do marcador proporcional (por área, não diâmetro) ao
 * total de turmas possíveis naquele ponto. Complementa a tabela agrupada —
 * não fabrica uma "duração" de turma que o dado não tem.
 */
export function LinhaDoTempoOportunidades({
  grupos,
  chavesAlternativa,
  onSelecionarDetalhe,
}: LinhaDoTempoOportunidadesProps) {
  const { dataMinMs, spanMs, maiorTotal, marcos } = useMemo(() => {
    const datas = grupos.flatMap((g) => g.itens.map((o) => Date.parse(o.data_inicio)));
    const min = Math.min(...datas);
    const max = Math.max(...datas);
    const maior = Math.max(1, ...grupos.flatMap((g) => g.itens.map((o) => o.total_turmas)));

    const listaMarcos: { ms: number; rotulo: string }[] = [];
    if (Number.isFinite(min) && Number.isFinite(max)) {
      const spanDias = (max - min) / 86_400_000;
      const passoDias = spanDias > 90 ? 30 : 7;
      let cursor = new Date(min);
      const fim = new Date(max);
      while (cursor.getTime() <= fim.getTime()) {
        listaMarcos.push({ ms: cursor.getTime(), rotulo: formatarData(cursor.toISOString()) });
        cursor = new Date(cursor.getTime() + passoDias * 86_400_000);
      }
    }

    return {
      dataMinMs: Number.isFinite(min) ? min : 0,
      spanMs: Number.isFinite(max) && Number.isFinite(min) && max > min ? max - min : 0,
      maiorTotal: maior,
      marcos: listaMarcos,
    };
  }, [grupos]);

  function posicao(dataIso: string): number {
    if (spanMs === 0) return 0.5;
    return (Date.parse(dataIso) - dataMinMs) / spanMs;
  }

  function diametro(totalTurmas: number): number {
    const fracao = Math.sqrt(totalTurmas) / Math.sqrt(maiorTotal);
    return DIAMETRO_MIN + fracao * (DIAMETRO_MAX - DIAMETRO_MIN);
  }

  return (
    <div className={styles.container}>
      <div className={styles.raias}>
        {marcos.length > 1 && (
          <div className={styles.grade} aria-hidden="true">
            {marcos.map((marco) => (
              <span
                key={marco.ms}
                className={styles.linhaGrade}
                style={{ left: `${((marco.ms - dataMinMs) / (spanMs || 1)) * 100}%` }}
              />
            ))}
          </div>
        )}

        {grupos.map((grupo) => (
          <div key={grupo.tipologiaNome} className={styles.raia}>
            <div className={styles.rotuloRaia}>{grupo.tipologiaNome}</div>
            <div className={styles.trilhaRaia}>
              {grupo.itens.map((o) => {
                const alternativa = o.instrutor_ids.some((id) =>
                  chavesAlternativa.has(`${id}::${o.data_inicio}`),
                );
                const tamanho = diametro(o.total_turmas);
                return (
                  <button
                    key={o.data_inicio}
                    type="button"
                    className={styles.marcador}
                    style={{ left: `${posicao(o.data_inicio) * 100}%` }}
                    onClick={() => onSelecionarDetalhe(grupo.tipologiaNome, o.data_inicio)}
                    aria-label={`${grupo.tipologiaNome}, ${formatarData(o.data_inicio)}, ${o.total_turmas} turma${o.total_turmas === 1 ? "" : "s"} possível${o.total_turmas === 1 ? "" : "eis"}${alternativa ? ", alternativa entre tipologias" : ""}`}
                    title={`${formatarData(o.data_inicio)} · ${o.total_turmas} turma(s) possível(is)`}
                  >
                    <span
                      className={[styles.ponto, alternativa ? styles.pontoAlternativa : ""].join(" ")}
                      style={{ width: tamanho, height: tamanho }}
                    />
                  </button>
                );
              })}
            </div>
          </div>
        ))}
      </div>

      {spanMs > 0 && (
        <div className={styles.legendaEixo}>
          <span>{formatarData(new Date(dataMinMs).toISOString())}</span>
          <span>{formatarData(new Date(dataMinMs + spanMs).toISOString())}</span>
        </div>
      )}
    </div>
  );
}

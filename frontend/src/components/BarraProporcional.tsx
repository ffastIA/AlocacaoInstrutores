import type { Tom } from "./tons";
import { coresDoTom } from "./tons";
import styles from "./BarraProporcional.module.css";

export interface SegmentoBarra {
  rotulo: string;
  valor: number;
  cor?: Tom;
}

interface BarraProporcionalProps {
  segmentos: SegmentoBarra[];
  /** Omitido = soma dos segmentos (caso "distribuição"). Para "medidor", defina o limite (ex.: 100). */
  maximo?: number;
  papel: "medidor" | "distribuicao";
  /** Nome da métrica, usado no aria-valuetext quando papel="medidor". */
  rotulo?: string;
  tamanho?: "padrao" | "compacta";
}

/**
 * Barra proporcional 100% CSS (sem lib de gráficos) para pesos, utilização e
 * distribuições. `papel="medidor"` expõe semântica de progressbar (razão
 * contra um limite); `papel="distribuicao"` é decorativa — o texto irmão ao
 * lado sempre carrega o valor exato.
 */
export function BarraProporcional({
  segmentos,
  maximo,
  papel,
  rotulo,
  tamanho = "padrao",
}: BarraProporcionalProps) {
  const total = segmentos.reduce((soma, s) => soma + Math.max(0, s.valor), 0);
  const limite = maximo ?? total;
  const trilha = Math.max(0, limite - total);

  const propsAcessibilidade =
    papel === "medidor"
      ? {
          role: "progressbar" as const,
          "aria-valuemin": 0,
          "aria-valuemax": limite,
          "aria-valuenow": total,
          "aria-valuetext": `${rotulo ? `${rotulo}: ` : ""}${total}${limite === 100 ? "%" : ""}`,
        }
      : { "aria-hidden": true as const };

  return (
    <div
      className={[styles.container, tamanho === "compacta" ? styles.compacta : styles.padrao].join(
        " ",
      )}
      {...propsAcessibilidade}
    >
      {segmentos.map((segmento, indice) =>
        segmento.valor > 0 ? (
          <span
            key={`${segmento.rotulo}-${indice}`}
            className={styles.segmento}
            style={{
              flexGrow: segmento.valor,
              backgroundColor: coresDoTom(segmento.cor ?? "primaria").cor,
            }}
            title={`${segmento.rotulo}: ${segmento.valor}`}
          />
        ) : null,
      )}
      {trilha > 0 && (
        <span
          className={styles.trilha}
          style={{
            flexGrow: trilha,
            backgroundColor:
              papel === "medidor" ? coresDoTom(segmentos[0]?.cor ?? "primaria").fundo : undefined,
          }}
        />
      )}
    </div>
  );
}

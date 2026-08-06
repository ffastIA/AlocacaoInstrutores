import type { ReactNode } from "react";
import type { Tom } from "./tons";
import { coresDoTom } from "./tons";
import styles from "./Selo.module.css";

interface SeloProps {
  tom?: Tom;
  icone?: boolean;
  children: ReactNode;
}

const ICONES: Record<Tom, string> = {
  info: "ℹ",
  sucesso: "✓",
  alerta: "!",
  erro: "✕",
  primaria: "●",
  neutro: "●",
};

/** Selo (chip) semântico para status curtos — reaproveita as cores do `Alert`. */
export function Selo({ tom = "neutro", icone = false, children }: SeloProps) {
  const cores = coresDoTom(tom);
  return (
    <span className={styles.selo} style={{ color: cores.cor, background: cores.fundo }}>
      {icone && (
        <span aria-hidden="true" className={styles.icone}>
          {ICONES[tom]}
        </span>
      )}
      {children}
    </span>
  );
}

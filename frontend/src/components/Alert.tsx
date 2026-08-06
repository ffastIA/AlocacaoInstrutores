import type { ReactNode } from "react";
import styles from "./Alert.module.css";

type Variante = "info" | "sucesso" | "alerta" | "erro";

interface AlertProps {
  variante?: Variante;
  titulo?: string;
  children: ReactNode;
}

/** Aviso nas variantes informação, sucesso, alerta e erro. */
export function Alert({ variante = "info", titulo, children }: AlertProps) {
  return (
    <div
      className={[styles.aviso, styles[variante]].join(" ")}
      role={variante === "erro" ? "alert" : "status"}
    >
      <span className={styles.icone} aria-hidden="true">
        {ICONES[variante]}
      </span>
      <div>
        {titulo && <p className={styles.titulo}>{titulo}</p>}
        <div className={styles.mensagem}>{children}</div>
      </div>
    </div>
  );
}

const ICONES: Record<Variante, string> = {
  info: "ℹ",
  sucesso: "✓",
  alerta: "!",
  erro: "✕",
};

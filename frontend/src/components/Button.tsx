import type { ButtonHTMLAttributes, ReactNode } from "react";
import styles from "./Button.module.css";

type Variante = "primaria" | "secundaria" | "destrutiva";

interface BotaoProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variante?: Variante;
  carregando?: boolean;
  children: ReactNode;
}

/** Botão com as variantes primária, secundária e destrutiva, e estado de carregamento. */
export function Button({
  variante = "primaria",
  carregando = false,
  disabled,
  children,
  className,
  ...props
}: BotaoProps) {
  return (
    <button
      className={[styles.botao, styles[variante], className].filter(Boolean).join(" ")}
      disabled={disabled ?? carregando}
      aria-busy={carregando}
      {...props}
    >
      {carregando && <span className={styles.spinner} aria-hidden="true" />}
      <span className={carregando ? styles.textoCarregando : undefined}>{children}</span>
    </button>
  );
}

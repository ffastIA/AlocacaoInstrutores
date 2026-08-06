import styles from "./Spinner.module.css";

interface SpinnerProps {
  rotulo?: string;
}

/** Indicador de carregamento, exibido no lugar do conteúdo enquanto ele não chega. */
export function Spinner({ rotulo = "Carregando…" }: SpinnerProps) {
  return (
    <div className={styles.container} role="status">
      <span className={styles.circulo} aria-hidden="true" />
      <span>{rotulo}</span>
    </div>
  );
}

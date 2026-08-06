import type { ReactNode } from "react";
import styles from "./EmptyState.module.css";

interface EmptyStateProps {
  titulo: string;
  descricao?: string;
  acao?: ReactNode;
}

/** Estado vazio: explica o que falta e sugere a próxima ação possível. */
export function EmptyState({ titulo, descricao, acao }: EmptyStateProps) {
  return (
    <div className={styles.container}>
      <p className={styles.titulo}>{titulo}</p>
      {descricao && <p className={styles.descricao}>{descricao}</p>}
      {acao && <div className={styles.acao}>{acao}</div>}
    </div>
  );
}

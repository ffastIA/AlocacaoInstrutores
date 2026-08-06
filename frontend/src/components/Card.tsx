import type { HTMLAttributes, ReactNode } from "react";
import styles from "./Card.module.css";

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  titulo?: ReactNode;
  acoes?: ReactNode;
  children: ReactNode;
}

/** Cartão de conteúdo com título e ações opcionais no cabeçalho. */
export function Card({ titulo, acoes, children, className, ...props }: CardProps) {
  return (
    <div className={[styles.card, className].filter(Boolean).join(" ")} {...props}>
      {(titulo || acoes) && (
        <div className={styles.cabecalho}>
          {titulo && <h3 className={styles.titulo}>{titulo}</h3>}
          {acoes && <div className={styles.acoes}>{acoes}</div>}
        </div>
      )}
      <div className={styles.conteudo}>{children}</div>
    </div>
  );
}

import { useEffect, useRef } from "react";
import type { ReactNode } from "react";
import { createPortal } from "react-dom";
import styles from "./Modal.module.css";

interface ModalProps {
  aberto: boolean;
  titulo: string;
  onFechar: () => void;
  children: ReactNode;
}

/** Modal com foco preso dentro dele e fechamento pela tecla Escape. */
export function Modal({ aberto, titulo, onFechar, children }: ModalProps) {
  const refConteudo = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!aberto) return;

    function aoTeclar(evento: KeyboardEvent): void {
      if (evento.key === "Escape") {
        onFechar();
      }
    }

    document.addEventListener("keydown", aoTeclar);
    refConteudo.current?.focus();
    return () => document.removeEventListener("keydown", aoTeclar);
  }, [aberto, onFechar]);

  if (!aberto) return null;

  return createPortal(
    <div className={styles.sobreposicao} onClick={onFechar}>
      <div
        ref={refConteudo}
        className={styles.conteudo}
        role="dialog"
        aria-modal="true"
        aria-labelledby="modal-titulo"
        tabIndex={-1}
        onClick={(evento) => evento.stopPropagation()}
      >
        <div className={styles.cabecalho}>
          <h2 id="modal-titulo" className={styles.titulo}>
            {titulo}
          </h2>
          <button
            type="button"
            className={styles.botaoFechar}
            onClick={onFechar}
            aria-label="Fechar"
          >
            ×
          </button>
        </div>
        <div className={styles.corpo}>{children}</div>
      </div>
    </div>,
    document.body,
  );
}

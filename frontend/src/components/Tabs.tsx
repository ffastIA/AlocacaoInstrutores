import styles from "./Tabs.module.css";

export interface AbaTab {
  id: string;
  rotulo: string;
}

interface TabsProps {
  abas: AbaTab[];
  abaAtiva: string;
  onSelecionar: (id: string) => void;
}

/** Navegação por abas, acessível via teclado (setas esquerda/direita). */
export function Tabs({ abas, abaAtiva, onSelecionar }: TabsProps) {
  function aoTeclar(evento: React.KeyboardEvent, indice: number): void {
    if (evento.key !== "ArrowRight" && evento.key !== "ArrowLeft") return;
    evento.preventDefault();
    const proximo =
      evento.key === "ArrowRight"
        ? (indice + 1) % abas.length
        : (indice - 1 + abas.length) % abas.length;
    onSelecionar(abas[proximo].id);
  }

  return (
    <div className={styles.lista} role="tablist">
      {abas.map((aba, indice) => (
        <button
          key={aba.id}
          type="button"
          role="tab"
          aria-selected={aba.id === abaAtiva}
          tabIndex={aba.id === abaAtiva ? 0 : -1}
          className={[styles.aba, aba.id === abaAtiva ? styles.abaAtiva : undefined]
            .filter(Boolean)
            .join(" ")}
          onClick={() => onSelecionar(aba.id)}
          onKeyDown={(evento) => aoTeclar(evento, indice)}
        >
          {aba.rotulo}
        </button>
      ))}
    </div>
  );
}

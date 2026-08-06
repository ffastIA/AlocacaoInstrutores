/**
 * Vocabulário de cor compartilhado entre `Selo` e `BarraProporcional` — mapeia
 * um tom semântico para os tokens de cor de `styles/tokens.css`. Um só lugar
 * evita que os dois componentes divirjam em qual token representa cada tom.
 */
export type Tom = "primaria" | "sucesso" | "alerta" | "erro" | "info" | "neutro";

interface CoresDoTom {
  cor: string;
  fundo: string;
}

const TONS: Record<Tom, CoresDoTom> = {
  primaria: { cor: "var(--color-primary)", fundo: "var(--color-primary-subtle)" },
  sucesso: { cor: "var(--color-success)", fundo: "var(--color-success-subtle)" },
  alerta: { cor: "var(--color-warning)", fundo: "var(--color-warning-subtle)" },
  erro: { cor: "var(--color-danger)", fundo: "var(--color-danger-subtle)" },
  info: { cor: "var(--color-info)", fundo: "var(--color-info-subtle)" },
  neutro: { cor: "var(--color-text-secondary)", fundo: "var(--color-border)" },
};

export function coresDoTom(tom: Tom): CoresDoTom {
  return TONS[tom];
}

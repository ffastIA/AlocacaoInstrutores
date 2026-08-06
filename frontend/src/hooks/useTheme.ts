import { useCallback, useEffect, useState } from "react";

export type Tema = "light" | "dark";

const CHAVE_ARMAZENAMENTO = "alocacao-instrutores:tema";

function lerTemaSalvo(): Tema | null {
  const valor = localStorage.getItem(CHAVE_ARMAZENAMENTO);
  return valor === "light" || valor === "dark" ? valor : null;
}

function aplicarTema(tema: Tema | null): void {
  const raiz = document.documentElement;
  if (tema === null) {
    // Sem escolha explícita: o CSS decide sozinho via prefers-color-scheme.
    raiz.removeAttribute("data-theme");
  } else {
    raiz.setAttribute("data-theme", tema);
  }
}

function temaPreferidoDoSistema(): Tema {
  return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

/**
 * Tema efetivo da interface, com alternância manual persistida.
 *
 * Sem escolha explícita do usuário, segue a preferência do sistema
 * operacional — inclusive reagindo a mudanças dela em tempo real.
 */
export function useTema(): { tema: Tema; escolhaExplicita: boolean; alternar: () => void } {
  const [escolha, setEscolha] = useState<Tema | null>(() => lerTemaSalvo());
  const [temaDoSistema, setTemaDoSistema] = useState<Tema>(() => temaPreferidoDoSistema());

  useEffect(() => {
    aplicarTema(escolha);
  }, [escolha]);

  useEffect(() => {
    const consulta = window.matchMedia("(prefers-color-scheme: dark)");
    const ouvinte = (evento: MediaQueryListEvent) => {
      setTemaDoSistema(evento.matches ? "dark" : "light");
    };
    consulta.addEventListener("change", ouvinte);
    return () => consulta.removeEventListener("change", ouvinte);
  }, []);

  const alternar = useCallback(() => {
    setEscolha((atual) => {
      const efetivo = atual ?? temaPreferidoDoSistema();
      const proximo: Tema = efetivo === "dark" ? "light" : "dark";
      localStorage.setItem(CHAVE_ARMAZENAMENTO, proximo);
      return proximo;
    });
  }, []);

  return {
    tema: escolha ?? temaDoSistema,
    escolhaExplicita: escolha !== null,
    alternar,
  };
}

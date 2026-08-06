import { useMemo, useState } from "react";
import type { ReactNode } from "react";
import styles from "./Table.module.css";

export interface ColunaTabela<Linha> {
  chave: string;
  titulo: string;
  renderizar: (linha: Linha) => ReactNode;
  ordenavel?: boolean;
  valorOrdenacao?: (linha: Linha) => string | number;
  numerica?: boolean;
}

interface TableProps<Linha> {
  colunas: ColunaTabela<Linha>[];
  linhas: Linha[];
  chaveLinha: (linha: Linha) => string | number;
}

type Direcao = "asc" | "desc";

/**
 * Tabela com cabeçalho fixo, ordenação por coluna e rolagem horizontal
 * contida no próprio contêiner — a página nunca rola lateralmente por causa
 * de uma tabela larga.
 */
export function Table<Linha>({ colunas, linhas, chaveLinha }: TableProps<Linha>) {
  const [ordenacao, setOrdenacao] = useState<{ chave: string; direcao: Direcao } | null>(null);

  const linhasOrdenadas = useMemo(() => {
    if (!ordenacao) return linhas;
    const coluna = colunas.find((c) => c.chave === ordenacao.chave);
    if (!coluna?.valorOrdenacao) return linhas;

    const copia = [...linhas];
    copia.sort((a, b) => {
      const valorA = coluna.valorOrdenacao!(a);
      const valorB = coluna.valorOrdenacao!(b);
      const comparacao = valorA < valorB ? -1 : valorA > valorB ? 1 : 0;
      return ordenacao.direcao === "asc" ? comparacao : -comparacao;
    });
    return copia;
  }, [linhas, ordenacao, colunas]);

  function alternarOrdenacao(chave: string): void {
    setOrdenacao((atual) => {
      if (atual?.chave !== chave) return { chave, direcao: "asc" };
      if (atual.direcao === "asc") return { chave, direcao: "desc" };
      return null;
    });
  }

  return (
    <div className={styles.container}>
      <table className={styles.tabela}>
        <thead>
          <tr>
            {colunas.map((coluna) => (
              <th
                key={coluna.chave}
                className={[styles.cabecalho, coluna.numerica ? styles.numerica : undefined]
                  .filter(Boolean)
                  .join(" ")}
                aria-sort={
                  ordenacao?.chave === coluna.chave
                    ? ordenacao.direcao === "asc"
                      ? "ascending"
                      : "descending"
                    : undefined
                }
              >
                {coluna.ordenavel ? (
                  <button
                    type="button"
                    className={styles.botaoOrdenar}
                    onClick={() => alternarOrdenacao(coluna.chave)}
                  >
                    {coluna.titulo}
                    <span className={styles.indicadorOrdenacao} aria-hidden="true">
                      {ordenacao?.chave === coluna.chave
                        ? ordenacao.direcao === "asc"
                          ? "▲"
                          : "▼"
                        : ""}
                    </span>
                  </button>
                ) : (
                  coluna.titulo
                )}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {linhasOrdenadas.map((linha) => (
            <tr key={chaveLinha(linha)}>
              {colunas.map((coluna) => (
                <td
                  key={coluna.chave}
                  className={coluna.numerica ? `${styles.numerica} tabular-nums` : undefined}
                >
                  {coluna.renderizar(linha)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

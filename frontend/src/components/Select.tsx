import { useId } from "react";
import type { SelectHTMLAttributes } from "react";
import styles from "./Field.module.css";

interface OpcaoSelect {
  valor: string;
  rotulo: string;
}

interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
  rotulo: string;
  opcoes: OpcaoSelect[];
  erro?: string;
}

/** Seleção com rótulo e mensagem de erro associados via aria. */
export function Select({ rotulo, opcoes, erro, id, className, ...props }: SelectProps) {
  const idGerado = useId();
  const idCampo = id ?? idGerado;
  const idErro = `${idCampo}-erro`;

  return (
    <div className={styles.grupo}>
      <label className={styles.rotulo} htmlFor={idCampo}>
        {rotulo}
      </label>
      <select
        id={idCampo}
        className={[styles.entrada, erro ? styles.comErro : undefined, className]
          .filter(Boolean)
          .join(" ")}
        aria-invalid={erro ? true : undefined}
        aria-describedby={erro ? idErro : undefined}
        {...props}
      >
        {opcoes.map((opcao) => (
          <option key={opcao.valor} value={opcao.valor}>
            {opcao.rotulo}
          </option>
        ))}
      </select>
      {erro && (
        <span id={idErro} className={styles.mensagemErro}>
          {erro}
        </span>
      )}
    </div>
  );
}

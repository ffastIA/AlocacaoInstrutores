import { useId } from "react";
import type { InputHTMLAttributes } from "react";
import styles from "./Field.module.css";

interface DateFieldProps extends Omit<InputHTMLAttributes<HTMLInputElement>, "type"> {
  rotulo: string;
  erro?: string;
}

/** Seletor de data única, usando o input nativo do navegador. */
export function DateField({ rotulo, erro, id, className, ...props }: DateFieldProps) {
  const idGerado = useId();
  const idCampo = id ?? idGerado;
  const idErro = `${idCampo}-erro`;

  return (
    <div className={styles.grupo}>
      <label className={styles.rotulo} htmlFor={idCampo}>
        {rotulo}
      </label>
      <input
        id={idCampo}
        type="date"
        className={[styles.entrada, "tabular-nums", erro ? styles.comErro : undefined, className]
          .filter(Boolean)
          .join(" ")}
        aria-invalid={erro ? true : undefined}
        aria-describedby={erro ? idErro : undefined}
        {...props}
      />
      {erro && (
        <span id={idErro} className={styles.mensagemErro}>
          {erro}
        </span>
      )}
    </div>
  );
}

import { useId } from "react";
import type { InputHTMLAttributes } from "react";
import styles from "./Field.module.css";

interface TextFieldProps extends InputHTMLAttributes<HTMLInputElement> {
  rotulo: string;
  erro?: string;
}

/** Campo de texto com rótulo e mensagem de erro associados via aria. */
export function TextField({ rotulo, erro, id, className, ...props }: TextFieldProps) {
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
        className={[styles.entrada, erro ? styles.comErro : undefined, className]
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

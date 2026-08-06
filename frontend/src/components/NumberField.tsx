import { useId } from "react";
import type { InputHTMLAttributes } from "react";
import styles from "./Field.module.css";

interface NumberFieldProps
  extends Omit<InputHTMLAttributes<HTMLInputElement>, "type" | "onChange"> {
  rotulo: string;
  erro?: string;
  onChange?: (valor: number | null) => void;
}

/** Campo numérico. `onChange` entrega o valor já convertido (ou null se vazio). */
export function NumberField({
  rotulo,
  erro,
  id,
  className,
  onChange,
  ...props
}: NumberFieldProps) {
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
        type="number"
        className={[styles.entrada, "tabular-nums", erro ? styles.comErro : undefined, className]
          .filter(Boolean)
          .join(" ")}
        aria-invalid={erro ? true : undefined}
        aria-describedby={erro ? idErro : undefined}
        onChange={(evento) => {
          const texto = evento.target.value;
          onChange?.(texto === "" ? null : Number(texto));
        }}
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

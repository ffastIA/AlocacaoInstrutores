import styles from "./DateRangeField.module.css";
import { DateField } from "./DateField";

interface DateRangeFieldProps {
  rotuloInicio?: string;
  rotuloFim?: string;
  valorInicio: string;
  valorFim: string;
  onChangeInicio: (valor: string) => void;
  onChangeFim: (valor: string) => void;
  erro?: string;
}

/** Par de campos de data para selecionar um intervalo (ex.: período simulado). */
export function DateRangeField({
  rotuloInicio = "De",
  rotuloFim = "Até",
  valorInicio,
  valorFim,
  onChangeInicio,
  onChangeFim,
  erro,
}: DateRangeFieldProps) {
  return (
    <div className={styles.faixa}>
      <DateField
        rotulo={rotuloInicio}
        value={valorInicio}
        onChange={(evento) => onChangeInicio(evento.target.value)}
        max={valorFim || undefined}
      />
      <DateField
        rotulo={rotuloFim}
        value={valorFim}
        onChange={(evento) => onChangeFim(evento.target.value)}
        min={valorInicio || undefined}
        erro={erro}
      />
    </div>
  );
}

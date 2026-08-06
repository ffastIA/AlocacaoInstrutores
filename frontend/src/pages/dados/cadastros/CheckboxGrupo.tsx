import styles from "./CheckboxGrupo.module.css";

interface OpcaoCheckbox {
  valor: string;
  rotulo: string;
}

interface CheckboxGrupoProps {
  rotulo: string;
  opcoes: OpcaoCheckbox[];
  selecionados: string[];
  onAlternar: (valor: string) => void;
  erro?: string;
}

/** Grupo de checkboxes para seleção múltipla (dias da semana, tipologias). */
export function CheckboxGrupo({
  rotulo,
  opcoes,
  selecionados,
  onAlternar,
  erro,
}: CheckboxGrupoProps) {
  return (
    <fieldset className={styles.grupo}>
      <legend className={styles.rotulo}>{rotulo}</legend>
      <div className={styles.opcoes}>
        {opcoes.map((opcao) => (
          <label key={opcao.valor} className={styles.opcao}>
            <input
              type="checkbox"
              checked={selecionados.includes(opcao.valor)}
              onChange={() => onAlternar(opcao.valor)}
            />
            {opcao.rotulo}
          </label>
        ))}
      </div>
      {erro && <span className={styles.mensagemErro}>{erro}</span>}
    </fieldset>
  );
}

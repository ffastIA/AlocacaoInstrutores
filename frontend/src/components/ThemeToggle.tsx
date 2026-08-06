import { useTema } from "../hooks/useTheme";
import styles from "./ThemeToggle.module.css";

/** Alterna entre tema claro e escuro, persistindo a escolha do usuário. */
export function ThemeToggle() {
  const { tema, alternar } = useTema();
  const proximoRotulo = tema === "dark" ? "Mudar para tema claro" : "Mudar para tema escuro";

  return (
    <button
      type="button"
      className={styles.botao}
      onClick={alternar}
      aria-label={proximoRotulo}
      title={proximoRotulo}
    >
      {tema === "dark" ? <IconeSol /> : <IconeLua />}
    </button>
  );
}

function IconeSol() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <circle cx="12" cy="12" r="4" stroke="currentColor" strokeWidth="2" />
      <path
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41"
      />
    </svg>
  );
}

function IconeLua() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path
        stroke="currentColor"
        strokeWidth="2"
        strokeLinejoin="round"
        d="M20 14.5A8.5 8.5 0 1 1 9.5 4a7 7 0 0 0 10.5 10.5Z"
      />
    </svg>
  );
}

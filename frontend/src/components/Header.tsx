import { ThemeToggle } from "./ThemeToggle";
import styles from "./Header.module.css";

export function Header() {
  return (
    <header className={styles.header}>
      <span className={styles.titulo}>Alocação de Instrutores</span>
      <ThemeToggle />
    </header>
  );
}

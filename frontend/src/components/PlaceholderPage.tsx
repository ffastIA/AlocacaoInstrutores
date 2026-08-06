import styles from "./PlaceholderPage.module.css";

interface PlaceholderPageProps {
  titulo: string;
  descricao: string;
}

/**
 * Espaço reservado para telas ainda não implementadas.
 *
 * Todas as rotas da aplicação já existem desde a fundação do frontend — as
 * changes de telas (`add-frontend-data-screens`,
 * `add-frontend-simulation-screens`) substituem este conteúdo pela tela real,
 * sem precisar mexer no roteamento.
 */
export function PlaceholderPage({ titulo, descricao }: PlaceholderPageProps) {
  return (
    <div className={styles.container}>
      <h1 className={styles.titulo}>{titulo}</h1>
      <p className={styles.descricao}>{descricao}</p>
    </div>
  );
}

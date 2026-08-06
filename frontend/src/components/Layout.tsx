import { Outlet } from "react-router-dom";
import { Alert } from "./Alert";
import { Button } from "./Button";
import { Header } from "./Header";
import { Sidebar } from "./Sidebar";
import { useSaudeBackend } from "../hooks/useSaudeBackend";
import styles from "./Layout.module.css";

/** Estrutura comum a todas as telas: cabeçalho, navegação e área de conteúdo. */
export function Layout() {
  const { estado, tentarNovamente } = useSaudeBackend();

  return (
    <div className={styles.raiz}>
      <Header />
      <div className={styles.corpo}>
        <Sidebar />
        <main className={styles.conteudo}>
          {estado === "indisponivel" && (
            <div className={styles.avisoServidor}>
              <Alert variante="erro" titulo="Não foi possível conectar ao servidor">
                <div className={styles.avisoConteudo}>
                  <span>
                    Verifique se o backend está em execução e tente novamente.
                  </span>
                  <Button variante="secundaria" onClick={tentarNovamente}>
                    Tentar novamente
                  </Button>
                </div>
              </Alert>
            </div>
          )}
          <Outlet />
        </main>
      </div>
    </div>
  );
}

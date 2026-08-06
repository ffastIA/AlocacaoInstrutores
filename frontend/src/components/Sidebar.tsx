import { NavLink } from "react-router-dom";
import { GRUPOS_NAVEGACAO } from "../config/navegacao";
import styles from "./Sidebar.module.css";

/** Navegação lateral, agrupada entre dados e simulação. */
export function Sidebar() {
  return (
    <nav className={styles.sidebar} aria-label="Navegação principal">
      {GRUPOS_NAVEGACAO.map((grupo) => (
        <div key={grupo.titulo} className={styles.grupo}>
          <h2 className={styles.tituloGrupo}>{grupo.titulo}</h2>
          <ul className={styles.lista}>
            {grupo.itens.map((item) => (
              <li key={item.caminho}>
                <NavLink
                  to={item.caminho}
                  className={({ isActive }) =>
                    [styles.link, isActive ? styles.linkAtivo : undefined]
                      .filter(Boolean)
                      .join(" ")
                  }
                >
                  {item.rotulo}
                </NavLink>
              </li>
            ))}
          </ul>
        </div>
      ))}
    </nav>
  );
}

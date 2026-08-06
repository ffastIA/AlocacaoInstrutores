import { useSearchParams } from "react-router-dom";
import { Tabs } from "../../components/Tabs";
import { InstrutoresTab } from "./cadastros/InstrutoresTab";
import { ProjetosTab } from "./cadastros/ProjetosTab";
import { TipologiasTab } from "./cadastros/TipologiasTab";
import styles from "./CadastrosPage.module.css";

const ABAS = [
  { id: "instrutores", rotulo: "Instrutores" },
  { id: "tipologias", rotulo: "Tipologias" },
  { id: "projetos", rotulo: "Projetos" },
];

const ABAS_VALIDAS = new Set(ABAS.map((a) => a.id));

/** Cadastros de domínio: instrutores, tipologias e projetos. */
export function CadastrosPage() {
  const [params, setParams] = useSearchParams();
  const abaParam = params.get("aba");
  const abaAtiva = abaParam && ABAS_VALIDAS.has(abaParam) ? abaParam : "instrutores";

  function selecionarAba(id: string): void {
    setParams({ aba: id });
  }

  return (
    <div className={styles.container}>
      <h1 className={styles.titulo}>Cadastros</h1>
      <Tabs abas={ABAS} abaAtiva={abaAtiva} onSelecionar={selecionarAba} />

      {abaAtiva === "instrutores" && <InstrutoresTab />}
      {abaAtiva === "tipologias" && <TipologiasTab />}
      {abaAtiva === "projetos" && <ProjetosTab />}
    </div>
  );
}

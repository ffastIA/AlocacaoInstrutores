import { Navigate, Route, Routes } from "react-router-dom";
import { Layout } from "./components/Layout";
import { CAMINHO_INICIAL } from "./config/navegacao";
import { CadastrosPage } from "./pages/dados/CadastrosPage";
import { DatasNaoLetivasPage } from "./pages/dados/DatasNaoLetivasPage";
import { ImportacaoPage } from "./pages/dados/ImportacaoPage";
import { SituacaoAtualPage } from "./pages/dados/SituacaoAtualPage";
import { NotFoundPage } from "./pages/NotFoundPage";
import { AgendaPage } from "./pages/simulacao/AgendaPage";
import { CenariosPage } from "./pages/simulacao/CenariosPage";
import { ComparacaoPage } from "./pages/simulacao/ComparacaoPage";
import { HistoricoPage } from "./pages/simulacao/HistoricoPage";
import { OportunidadesPage } from "./pages/simulacao/OportunidadesPage";

export function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<Navigate to={CAMINHO_INICIAL} replace />} />

        <Route path="dados/importacao" element={<ImportacaoPage />} />
        <Route path="dados/cadastros" element={<CadastrosPage />} />
        <Route path="dados/situacao-atual" element={<SituacaoAtualPage />} />
        <Route path="dados/datas-nao-letivas" element={<DatasNaoLetivasPage />} />

        <Route path="simulacao/cenarios" element={<CenariosPage />} />
        <Route path="simulacao/oportunidades" element={<OportunidadesPage />} />
        <Route path="simulacao/agenda" element={<AgendaPage />} />
        <Route path="simulacao/comparacao" element={<ComparacaoPage />} />
        <Route path="simulacao/historico" element={<HistoricoPage />} />

        <Route path="*" element={<NotFoundPage />} />
      </Route>
    </Routes>
  );
}

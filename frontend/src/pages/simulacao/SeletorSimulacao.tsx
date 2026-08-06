import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../../api/cliente";
import { ApiError } from "../../api/erros";
import type { Cenario, Simulacao } from "../../api/types";
import { Alert } from "../../components/Alert";
import { EmptyState } from "../../components/EmptyState";
import { Select } from "../../components/Select";
import { Spinner } from "../../components/Spinner";
import { formatarDataHora } from "../../utils/data";
import styles from "./SeletorSimulacao.module.css";

interface SeletorSimulacaoProps {
  onSelecionar: (simulacaoId: number) => void;
}

/** Escolha de simulação quando a tela é acessada sem um contexto definido. */
export function SeletorSimulacao({ onSelecionar }: SeletorSimulacaoProps) {
  const [simulacoes, setSimulacoes] = useState<Simulacao[] | null>(null);
  const [cenarios, setCenarios] = useState<Cenario[]>([]);
  const [erro, setErro] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([api.get<Simulacao[]>("/simulacoes"), api.get<Cenario[]>("/cenarios")])
      .then(([listaSimulacoes, listaCenarios]) => {
        setSimulacoes(listaSimulacoes);
        setCenarios(listaCenarios);
      })
      .catch((excecao) => {
        setErro(excecao instanceof ApiError ? excecao.message : "Falha ao carregar simulações.");
      });
  }, []);

  if (erro) return <Alert variante="erro">{erro}</Alert>;
  if (simulacoes === null) return <Spinner rotulo="Carregando simulações…" />;

  const concluidas = simulacoes.filter((s) => s.status === "concluida");

  if (concluidas.length === 0) {
    return (
      <EmptyState
        titulo="Nenhuma simulação concluída"
        descricao="Execute um cenário para ver o resultado aqui."
        acao={<Link to="/simulacao/cenarios">Ir para cenários</Link>}
      />
    );
  }

  return (
    <div className={styles.container}>
      <Select
        rotulo="Selecione uma simulação concluída"
        opcoes={[
          { valor: "", rotulo: "Selecione…" },
          ...concluidas.map((s) => ({
            valor: String(s.id),
            rotulo: `#${s.id} — ${cenarios.find((c) => c.id === s.cenario_id)?.nome ?? `cenário ${s.cenario_id}`} (${formatarDataHora(s.iniciado_em)})`,
          })),
        ]}
        onChange={(e) => e.target.value && onSelecionar(Number(e.target.value))}
      />
    </div>
  );
}

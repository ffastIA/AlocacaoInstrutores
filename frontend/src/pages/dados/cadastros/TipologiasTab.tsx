import { useEffect, useState } from "react";
import { api } from "../../../api/cliente";
import { ApiError } from "../../../api/erros";
import type { Tipologia, TipologiaIn } from "../../../api/types";
import { Alert } from "../../../components/Alert";
import { Button } from "../../../components/Button";
import { Modal } from "../../../components/Modal";
import { NumberField } from "../../../components/NumberField";
import { Spinner } from "../../../components/Spinner";
import { Table } from "../../../components/Table";
import type { ColunaTabela } from "../../../components/Table";
import { TextField } from "../../../components/TextField";
import styles from "./TipologiasTab.module.css";

interface FormState {
  carga_horaria_total_horas: number | null;
  horas_por_encontro: number | null;
  descricao: string;
}

export function TipologiasTab() {
  const [tipologias, setTipologias] = useState<Tipologia[] | null>(null);
  const [erroCarga, setErroCarga] = useState<string | null>(null);

  const [editando, setEditando] = useState<Tipologia | null>(null);
  const [form, setForm] = useState<FormState>({
    carga_horaria_total_horas: null,
    horas_por_encontro: null,
    descricao: "",
  });
  const [erroForm, setErroForm] = useState<string | null>(null);
  const [salvando, setSalvando] = useState(false);

  async function carregar(): Promise<void> {
    try {
      setTipologias(await api.get<Tipologia[]>("/tipologias"));
    } catch (excecao) {
      setErroCarga(excecao instanceof ApiError ? excecao.message : "Falha ao carregar tipologias.");
    }
  }

  useEffect(() => {
    void carregar();
  }, []);

  function abrirEdicao(tipologia: Tipologia): void {
    setEditando(tipologia);
    setForm({
      carga_horaria_total_horas: tipologia.carga_horaria_total_horas,
      horas_por_encontro: tipologia.horas_por_encontro,
      descricao: tipologia.descricao ?? "",
    });
    setErroForm(null);
  }

  function fechar(): void {
    setEditando(null);
    setErroForm(null);
  }

  const encontrosPrevistos =
    form.carga_horaria_total_horas && form.horas_por_encontro
      ? form.carga_horaria_total_horas / form.horas_por_encontro
      : null;
  const divisivel = encontrosPrevistos === null || Number.isInteger(encontrosPrevistos);

  async function salvar(): Promise<void> {
    if (!editando) return;
    setErroForm(null);

    if (!divisivel) {
      setErroForm(
        `A carga horária total não é múltiplo exato das horas por encontro: resultaria em ${encontrosPrevistos?.toFixed(2)} encontros.`,
      );
      return;
    }

    const dados: TipologiaIn = {
      nome: editando.nome,
      carga_horaria_total_horas: form.carga_horaria_total_horas,
      horas_por_encontro: form.horas_por_encontro,
      descricao: form.descricao.trim() || null,
    };

    setSalvando(true);
    try {
      await api.put(`/tipologias/${editando.id}`, dados);
      fechar();
      await carregar();
    } catch (excecao) {
      setErroForm(excecao instanceof ApiError ? excecao.message : "Não foi possível salvar.");
    } finally {
      setSalvando(false);
    }
  }

  if (erroCarga) return <Alert variante="erro">{erroCarga}</Alert>;
  if (tipologias === null) return <Spinner rotulo="Carregando tipologias…" />;

  const pendentes = tipologias.filter((t) => !t.configurada);

  const colunas: ColunaTabela<Tipologia>[] = [
    {
      chave: "nome",
      titulo: "Nome",
      ordenavel: true,
      valorOrdenacao: (t) => t.nome,
      renderizar: (t) => (
        <button type="button" className={styles.linkNome} onClick={() => abrirEdicao(t)}>
          {t.nome}
        </button>
      ),
    },
    {
      chave: "status",
      titulo: "Status",
      renderizar: (t) => {
        if (!t.configurada) {
          return <span className={styles.marcaBloqueio}>Pendente — bloqueia simulação</span>;
        }
        if (t.total_instrutores === 0) {
          return <span className={styles.marcaAlerta}>Nunca ofertável (sem instrutor apto)</span>;
        }
        return <span className={styles.marcaOk}>Configurada</span>;
      },
    },
    { chave: "carga_total", titulo: "Carga total (h)", numerica: true, renderizar: (t) => t.carga_horaria_total_horas ?? "—" },
    { chave: "horas_encontro", titulo: "Horas/encontro", numerica: true, renderizar: (t) => t.horas_por_encontro ?? "—" },
    { chave: "num_encontros", titulo: "Encontros", numerica: true, renderizar: (t) => t.num_encontros ?? "—" },
    { chave: "instrutores", titulo: "Instrutores aptos", numerica: true, renderizar: (t) => t.total_instrutores },
  ];

  return (
    <div className={styles.container}>
      {pendentes.length > 0 && (
        <Alert variante="alerta" titulo="Tipologias pendentes">
          {pendentes.length} tipologia(s) sem carga horária configurada. A simulação
          permanece bloqueada até que sejam configuradas: {pendentes.map((t) => t.nome).join(", ")}.
        </Alert>
      )}

      <Table colunas={colunas} linhas={tipologias} chaveLinha={(t) => t.id} />

      <Modal aberto={editando !== null} titulo="Configurar tipologia" onFechar={fechar}>
        {erroForm && (
          <Alert variante="erro" titulo="Não foi possível salvar">
            {erroForm}
          </Alert>
        )}
        <div className={styles.form}>
          <NumberField
            rotulo="Carga horária total (h)"
            value={form.carga_horaria_total_horas ?? ""}
            min={24}
            max={60}
            onChange={(valor) => setForm((f) => ({ ...f, carga_horaria_total_horas: valor }))}
          />
          <NumberField
            rotulo="Horas por encontro"
            value={form.horas_por_encontro ?? ""}
            min={1}
            step={0.5}
            onChange={(valor) => setForm((f) => ({ ...f, horas_por_encontro: valor }))}
          />
          {encontrosPrevistos !== null && (
            <p className={divisivel ? styles.previaEncontros : styles.previaEncontrosErro}>
              {divisivel
                ? `${encontrosPrevistos} encontro(s) no total.`
                : `Não fecha em número inteiro de encontros (${encontrosPrevistos.toFixed(2)}).`}
            </p>
          )}
          <TextField
            rotulo="Descrição"
            value={form.descricao}
            onChange={(e) => setForm((f) => ({ ...f, descricao: e.target.value }))}
          />
          <div className={styles.acoesForm}>
            <Button variante="secundaria" onClick={fechar} disabled={salvando}>
              Cancelar
            </Button>
            <Button onClick={salvar} carregando={salvando} disabled={!divisivel}>
              Salvar
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}

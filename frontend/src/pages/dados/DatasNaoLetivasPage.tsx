import { useEffect, useState } from "react";
import { api } from "../../api/cliente";
import { ApiError } from "../../api/erros";
import type {
  DataNaoLetiva,
  DataNaoLetivaIn,
  DatasNaoLetivasLista,
  Projeto,
  TipoDataNaoLetiva,
} from "../../api/types";
import { Alert } from "../../components/Alert";
import { Button } from "../../components/Button";
import { ConfirmDialog } from "../../components/ConfirmDialog";
import { DateRangeField } from "../../components/DateRangeField";
import { EmptyState } from "../../components/EmptyState";
import { Modal } from "../../components/Modal";
import { Select } from "../../components/Select";
import { Spinner } from "../../components/Spinner";
import { Table } from "../../components/Table";
import type { ColunaTabela } from "../../components/Table";
import { TextField } from "../../components/TextField";
import styles from "./DatasNaoLetivasPage.module.css";

const TIPOS: { valor: TipoDataNaoLetiva; rotulo: string }[] = [
  { valor: "feriado", rotulo: "Feriado" },
  { valor: "recesso", rotulo: "Recesso" },
  { valor: "ferias", rotulo: "Férias" },
];

const DIAS_SEM_EFEITO = new Set([0, 5, 6]); // domingo, sexta, sábado (Date.getDay())

function cobreApenasDiasSemEfeito(dataInicio: string, dataFim: string): boolean {
  const atual = new Date(`${dataInicio}T00:00:00`);
  const fim = new Date(`${dataFim}T00:00:00`);
  while (atual <= fim) {
    if (!DIAS_SEM_EFEITO.has(atual.getDay())) return false;
    atual.setDate(atual.getDate() + 1);
  }
  return true;
}

interface FormState {
  data_inicio: string;
  data_fim: string;
  descricao: string;
  tipo: TipoDataNaoLetiva;
  projeto_id: string;
}

function formVazio(): FormState {
  return { data_inicio: "", data_fim: "", descricao: "", tipo: "feriado", projeto_id: "" };
}

/** Calendário de feriados, recessos e férias — sem efeito no cálculo na v1. */
export function DatasNaoLetivasPage() {
  const [itens, setItens] = useState<DataNaoLetiva[] | null>(null);
  const [aviso, setAviso] = useState<string>("");
  const [projetos, setProjetos] = useState<Projeto[]>([]);
  const [erroCarga, setErroCarga] = useState<string | null>(null);

  const [filtroDe, setFiltroDe] = useState("");
  const [filtroAte, setFiltroAte] = useState("");

  const [modalAberto, setModalAberto] = useState(false);
  const [editando, setEditando] = useState<DataNaoLetiva | null>(null);
  const [form, setForm] = useState<FormState>(formVazio());
  const [erroForm, setErroForm] = useState<string | null>(null);
  const [salvando, setSalvando] = useState(false);
  const [confirmacaoSalvo, setConfirmacaoSalvo] = useState(false);

  const [removendo, setRemovendo] = useState<DataNaoLetiva | null>(null);
  const [confirmandoRemocao, setConfirmandoRemocao] = useState(false);

  async function carregar(): Promise<void> {
    try {
      const params = new URLSearchParams();
      if (filtroDe) params.set("de", filtroDe);
      if (filtroAte) params.set("ate", filtroAte);
      const query = params.toString();
      const [lista, listaProjetos] = await Promise.all([
        api.get<DatasNaoLetivasLista>(`/datas-nao-letivas${query ? `?${query}` : ""}`),
        api.get<Projeto[]>("/projetos"),
      ]);
      setItens(lista.itens);
      setAviso(lista.aviso);
      setProjetos(listaProjetos);
    } catch (excecao) {
      setErroCarga(excecao instanceof ApiError ? excecao.message : "Falha ao carregar as datas não letivas.");
    }
  }

  useEffect(() => {
    void carregar();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filtroDe, filtroAte]);

  function abrirNova(): void {
    setEditando(null);
    setForm(formVazio());
    setErroForm(null);
    setConfirmacaoSalvo(false);
    setModalAberto(true);
  }

  function abrirEdicao(item: DataNaoLetiva): void {
    setEditando(item);
    setForm({
      data_inicio: item.data_inicio,
      data_fim: item.data_fim === item.data_inicio ? "" : item.data_fim,
      descricao: item.descricao,
      tipo: item.tipo,
      projeto_id: item.projeto_id ? String(item.projeto_id) : "",
    });
    setErroForm(null);
    setConfirmacaoSalvo(false);
    setModalAberto(true);
  }

  function fechar(): void {
    setModalAberto(false);
    setErroForm(null);
  }

  async function salvar(): Promise<void> {
    setErroForm(null);

    if (!form.data_inicio) {
      setErroForm("Informe a data de início.");
      return;
    }
    if (!form.descricao.trim()) {
      setErroForm("Informe a descrição.");
      return;
    }
    if (form.data_fim && form.data_fim < form.data_inicio) {
      setErroForm("A data de término é anterior à data de início.");
      return;
    }

    const dados: DataNaoLetivaIn = {
      data_inicio: form.data_inicio,
      data_fim: form.data_fim || null,
      descricao: form.descricao.trim(),
      tipo: form.tipo,
      projeto_id: form.projeto_id ? Number(form.projeto_id) : null,
    };

    setSalvando(true);
    try {
      if (editando) {
        await api.put(`/datas-nao-letivas/${editando.id}`, dados);
      } else {
        await api.post("/datas-nao-letivas", dados);
      }
      setConfirmacaoSalvo(true);
      await carregar();
    } catch (excecao) {
      setErroForm(excecao instanceof ApiError ? excecao.message : "Não foi possível salvar.");
    } finally {
      setSalvando(false);
    }
  }

  async function confirmarRemocao(): Promise<void> {
    if (!removendo) return;
    setConfirmandoRemocao(true);
    try {
      await api.delete(`/datas-nao-letivas/${removendo.id}`);
      setRemovendo(null);
      await carregar();
    } catch (excecao) {
      setErroCarga(excecao instanceof ApiError ? excecao.message : "Não foi possível remover.");
    } finally {
      setConfirmandoRemocao(false);
    }
  }

  if (erroCarga) return <Alert variante="erro">{erroCarga}</Alert>;
  if (itens === null) return <Spinner rotulo="Carregando datas não letivas…" />;

  const colunas: ColunaTabela<DataNaoLetiva>[] = [
    {
      chave: "descricao",
      titulo: "Descrição",
      renderizar: (item) => (
        <button type="button" className={styles.linkNome} onClick={() => abrirEdicao(item)}>
          {item.descricao}
        </button>
      ),
    },
    {
      chave: "intervalo",
      titulo: "Intervalo",
      ordenavel: true,
      valorOrdenacao: (item) => item.data_inicio,
      renderizar: (item) =>
        item.data_inicio === item.data_fim
          ? item.data_inicio
          : `${item.data_inicio} a ${item.data_fim}`,
    },
    {
      chave: "tipo",
      titulo: "Tipo",
      renderizar: (item) => TIPOS.find((t) => t.valor === item.tipo)?.rotulo ?? item.tipo,
    },
    {
      chave: "projeto",
      titulo: "Projeto",
      renderizar: (item) => item.projeto_nome ?? "Todos os projetos",
    },
    {
      chave: "efeito",
      titulo: "",
      renderizar: (item) =>
        cobreApenasDiasSemEfeito(item.data_inicio, item.data_fim) ? (
          <span className={styles.marcaSemEfeito}>Sem efeito prático (sexta/fim de semana)</span>
        ) : null,
    },
    {
      chave: "acoes",
      titulo: "",
      renderizar: (item) => (
        <button type="button" className={styles.linkRemover} onClick={() => setRemovendo(item)}>
          Remover
        </button>
      ),
    },
  ];

  return (
    <div className={styles.container}>
      <div className={styles.cabecalho}>
        <h1 className={styles.titulo}>Calendário de Datas Não Letivas</h1>
        <Button onClick={abrirNova}>Novo registro</Button>
      </div>

      <Alert variante="alerta" titulo="Sem efeito no cálculo das simulações">
        {aviso ||
          "Estes dados são registrados para uso futuro e ainda não impactam o cálculo dos calendários."}
      </Alert>

      <div className={styles.filtros}>
        <DateRangeField
          rotuloInicio="De"
          rotuloFim="Até"
          valorInicio={filtroDe}
          valorFim={filtroAte}
          onChangeInicio={setFiltroDe}
          onChangeFim={setFiltroAte}
        />
      </div>

      {itens.length === 0 ? (
        <EmptyState
          titulo="Nenhuma data não letiva cadastrada"
          descricao="Importe a planilha de datas não letivas ou cadastre manualmente."
        />
      ) : (
        <Table colunas={colunas} linhas={itens} chaveLinha={(item) => item.id} />
      )}

      <Modal
        aberto={modalAberto}
        titulo={editando ? "Editar data não letiva" : "Novo registro"}
        onFechar={fechar}
      >
        {erroForm && (
          <Alert variante="erro" titulo="Não foi possível salvar">
            {erroForm}
          </Alert>
        )}
        {confirmacaoSalvo && (
          <Alert variante="sucesso" titulo="Registro salvo">
            Este registro ainda não altera os resultados das simulações.
          </Alert>
        )}
        <div className={styles.form}>
          <DateRangeField
            rotuloInicio="Data de início"
            rotuloFim="Data de término (opcional)"
            valorInicio={form.data_inicio}
            valorFim={form.data_fim}
            onChangeInicio={(valor) => setForm((f) => ({ ...f, data_inicio: valor }))}
            onChangeFim={(valor) => setForm((f) => ({ ...f, data_fim: valor }))}
          />
          <p className={styles.dicaIntervalo}>
            Deixe a data de término vazia para registrar um único dia.
          </p>
          <TextField
            rotulo="Descrição"
            value={form.descricao}
            onChange={(e) => setForm((f) => ({ ...f, descricao: e.target.value }))}
          />
          <Select
            rotulo="Tipo"
            opcoes={TIPOS.map((t) => ({ valor: t.valor, rotulo: t.rotulo }))}
            value={form.tipo}
            onChange={(e) => setForm((f) => ({ ...f, tipo: e.target.value as TipoDataNaoLetiva }))}
          />
          <Select
            rotulo="Projeto (opcional)"
            opcoes={[
              { valor: "", rotulo: "Todos os projetos" },
              ...projetos.map((p) => ({ valor: String(p.id), rotulo: p.nome })),
            ]}
            value={form.projeto_id}
            onChange={(e) => setForm((f) => ({ ...f, projeto_id: e.target.value }))}
          />
          {!form.projeto_id && (
            <p className={styles.dicaIntervalo}>
              Sem projeto selecionado, o registro se aplica a todos os projetos.
            </p>
          )}
          <div className={styles.acoesForm}>
            <Button variante="secundaria" onClick={fechar} disabled={salvando}>
              Fechar
            </Button>
            <Button onClick={salvar} carregando={salvando}>
              Salvar
            </Button>
          </div>
        </div>
      </Modal>

      <ConfirmDialog
        aberto={removendo !== null}
        titulo="Remover data não letiva"
        mensagem={removendo ? `Remover o registro "${removendo.descricao}"?` : ""}
        confirmando={confirmandoRemocao}
        onConfirmar={confirmarRemocao}
        onCancelar={() => setRemovendo(null)}
      />
    </div>
  );
}

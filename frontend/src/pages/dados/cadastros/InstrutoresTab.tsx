import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../../../api/cliente";
import { ApiError } from "../../../api/erros";
import type { Instrutor, InstrutorIn, Projeto, Tipologia, Turno } from "../../../api/types";
import { Alert } from "../../../components/Alert";
import { Button } from "../../../components/Button";
import { EmptyState } from "../../../components/EmptyState";
import { Modal } from "../../../components/Modal";
import { Select } from "../../../components/Select";
import { Spinner } from "../../../components/Spinner";
import { Table } from "../../../components/Table";
import type { ColunaTabela } from "../../../components/Table";
import { TextField } from "../../../components/TextField";
import { CheckboxGrupo } from "./CheckboxGrupo";
import styles from "./InstrutoresTab.module.css";

const TURNOS: { valor: Turno; rotulo: string }[] = [
  { valor: "manha_1", rotulo: "Manhã 1" },
  { valor: "manha_2", rotulo: "Manhã 2" },
  { valor: "tarde_1", rotulo: "Tarde 1" },
  { valor: "tarde_2", rotulo: "Tarde 2" },
  { valor: "noite", rotulo: "Noite" },
];

const ROTULO_TURNO: Record<Turno, string> = Object.fromEntries(
  TURNOS.map((t) => [t.valor, t.rotulo]),
) as Record<Turno, string>;

const DIAS: { valor: string; rotulo: string }[] = [
  { valor: "2", rotulo: "Segunda" },
  { valor: "3", rotulo: "Terça" },
  { valor: "4", rotulo: "Quarta" },
  { valor: "5", rotulo: "Quinta" },
  { valor: "6", rotulo: "Sexta (reposição)" },
];

interface FormState {
  nome: string;
  projeto_id: string;
  turnos: string[];
  dias_semana: string[];
  tipologia_ids: string[];
  observacao: string;
  ativo: boolean;
}

function formVazio(): FormState {
  return {
    nome: "",
    projeto_id: "",
    turnos: [],
    dias_semana: [],
    tipologia_ids: [],
    observacao: "",
    ativo: true,
  };
}

function formDeInstrutor(instrutor: Instrutor, tipologias: Tipologia[]): FormState {
  const idsPorNome = new Map(tipologias.map((t) => [t.nome, String(t.id)]));
  return {
    nome: instrutor.nome,
    projeto_id: String(instrutor.projeto_id),
    turnos: instrutor.turnos,
    dias_semana: instrutor.dias_semana.map(String),
    tipologia_ids: instrutor.tipologias
      .map((nome) => idsPorNome.get(nome))
      .filter((id): id is string => id !== undefined),
    observacao: instrutor.observacao ?? "",
    ativo: instrutor.ativo,
  };
}

export function InstrutoresTab() {
  const [instrutores, setInstrutores] = useState<Instrutor[] | null>(null);
  const [projetos, setProjetos] = useState<Projeto[]>([]);
  const [tipologias, setTipologias] = useState<Tipologia[]>([]);
  const [erroCarga, setErroCarga] = useState<string | null>(null);

  const [filtroProjeto, setFiltroProjeto] = useState("");
  const [filtroTipologia, setFiltroTipologia] = useState("");

  const [instrutorEditando, setInstrutorEditando] = useState<Instrutor | null>(null);
  const [form, setForm] = useState<FormState>(formVazio());
  const [erroForm, setErroForm] = useState<string | null>(null);
  const [salvando, setSalvando] = useState(false);

  async function carregar(): Promise<void> {
    try {
      const params = new URLSearchParams();
      if (filtroProjeto) params.set("projeto_id", filtroProjeto);
      if (filtroTipologia) params.set("tipologia_id", filtroTipologia);
      const query = params.toString();
      const [listaInstrutores, listaProjetos, listaTipologias] = await Promise.all([
        api.get<Instrutor[]>(`/instrutores${query ? `?${query}` : ""}`),
        api.get<Projeto[]>("/projetos"),
        api.get<Tipologia[]>("/tipologias"),
      ]);
      setInstrutores(listaInstrutores);
      setProjetos(listaProjetos);
      setTipologias(listaTipologias);
    } catch (excecao) {
      setErroCarga(excecao instanceof ApiError ? excecao.message : "Falha ao carregar instrutores.");
    }
  }

  useEffect(() => {
    void carregar();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filtroProjeto, filtroTipologia]);

  function abrirEdicao(instrutor: Instrutor): void {
    setInstrutorEditando(instrutor);
    setForm(formDeInstrutor(instrutor, tipologias));
    setErroForm(null);
  }

  function fechar(): void {
    setInstrutorEditando(null);
    setErroForm(null);
  }

  function alternarTurno(valor: string): void {
    setForm((atual) => ({
      ...atual,
      turnos: atual.turnos.includes(valor)
        ? atual.turnos.filter((t) => t !== valor)
        : [...atual.turnos, valor],
    }));
  }

  function alternarDia(valor: string): void {
    setForm((atual) => ({
      ...atual,
      dias_semana: atual.dias_semana.includes(valor)
        ? atual.dias_semana.filter((d) => d !== valor)
        : [...atual.dias_semana, valor],
    }));
  }

  function alternarTipologia(valor: string): void {
    setForm((atual) => ({
      ...atual,
      tipologia_ids: atual.tipologia_ids.includes(valor)
        ? atual.tipologia_ids.filter((t) => t !== valor)
        : [...atual.tipologia_ids, valor],
    }));
  }

  async function salvar(): Promise<void> {
    if (instrutorEditando === null) return;
    setErroForm(null);

    if (!form.nome.trim()) {
      setErroForm("Informe o nome do instrutor.");
      return;
    }
    if (!form.projeto_id) {
      setErroForm("Selecione o projeto.");
      return;
    }
    if (form.turnos.length === 0) {
      setErroForm("Selecione ao menos um slot de turno.");
      return;
    }
    if (form.dias_semana.length === 0) {
      setErroForm("Selecione ao menos um dia da semana.");
      return;
    }
    if (form.tipologia_ids.length === 0) {
      setErroForm("Selecione ao menos uma tipologia.");
      return;
    }

    const dados: InstrutorIn = {
      nome: form.nome.trim(),
      projeto_id: Number(form.projeto_id),
      turnos: form.turnos as Turno[],
      dias_semana: form.dias_semana.map(Number),
      tipologia_ids: form.tipologia_ids.map(Number),
      observacao: form.observacao.trim() || null,
      ativo: form.ativo,
    };

    setSalvando(true);
    try {
      await api.put(`/instrutores/${instrutorEditando.id}`, dados);
      fechar();
      await carregar();
    } catch (excecao) {
      setErroForm(excecao instanceof ApiError ? excecao.message : "Não foi possível salvar.");
    } finally {
      setSalvando(false);
    }
  }

  const colunas: ColunaTabela<Instrutor>[] = [
    {
      chave: "nome",
      titulo: "Nome",
      ordenavel: true,
      valorOrdenacao: (i) => i.nome,
      renderizar: (i) => (
        <button type="button" className={styles.linkNome} onClick={() => abrirEdicao(i)}>
          {i.nome}
        </button>
      ),
    },
    { chave: "projeto", titulo: "Projeto", renderizar: (i) => i.projeto_nome },
    {
      chave: "turnos",
      titulo: "Turnos",
      renderizar: (i) => i.turnos.map((t) => ROTULO_TURNO[t]).join(", "),
    },
    {
      chave: "dias",
      titulo: "Dias",
      renderizar: (i) =>
        i.dias_semana
          .map((d) => DIAS.find((opt) => opt.valor === String(d))?.rotulo.slice(0, 3))
          .join(", "),
    },
    { chave: "tipologias", titulo: "Tipologias", renderizar: (i) => i.tipologias.join(", ") },
    { chave: "ativo", titulo: "Ativo", renderizar: (i) => (i.ativo ? "Sim" : "Não") },
  ];

  if (erroCarga) return <Alert variante="erro">{erroCarga}</Alert>;
  if (instrutores === null) return <Spinner rotulo="Carregando instrutores…" />;

  return (
    <div className={styles.container}>
      <div className={styles.barraFiltros}>
        <Select
          rotulo="Projeto"
          opcoes={[{ valor: "", rotulo: "Todos" }, ...projetos.map((p) => ({ valor: String(p.id), rotulo: p.nome }))]}
          value={filtroProjeto}
          onChange={(e) => setFiltroProjeto(e.target.value)}
        />
        <Select
          rotulo="Tipologia"
          opcoes={[{ valor: "", rotulo: "Todas" }, ...tipologias.map((t) => ({ valor: String(t.id), rotulo: t.nome }))]}
          value={filtroTipologia}
          onChange={(e) => setFiltroTipologia(e.target.value)}
        />
      </div>

      {instrutores.length === 0 ? (
        <EmptyState
          titulo="Nenhum instrutor cadastrado"
          descricao="Importe a planilha de instrutores para começar."
          acao={<Link to="/dados/importacao">Ir para importação</Link>}
        />
      ) : (
        <Table colunas={colunas} linhas={instrutores} chaveLinha={(i) => i.id} />
      )}

      <Modal
        aberto={instrutorEditando !== null}
        titulo="Editar instrutor"
        onFechar={fechar}
      >
        {erroForm && (
          <Alert variante="erro" titulo="Não foi possível salvar">
            {erroForm}
          </Alert>
        )}
        <div className={styles.form}>
          <TextField
            rotulo="Nome"
            value={form.nome}
            onChange={(e) => setForm((f) => ({ ...f, nome: e.target.value }))}
          />
          <Select
            rotulo="Projeto"
            opcoes={[{ valor: "", rotulo: "Selecione…" }, ...projetos.map((p) => ({ valor: String(p.id), rotulo: p.nome }))]}
            value={form.projeto_id}
            onChange={(e) => setForm((f) => ({ ...f, projeto_id: e.target.value }))}
          />

          <CheckboxGrupo
            rotulo="Slots de turno (manhã e tarde têm 2 cada; noite tem 1)"
            opcoes={TURNOS}
            selecionados={form.turnos}
            onAlternar={alternarTurno}
          />

          <CheckboxGrupo
            rotulo="Dias da semana"
            opcoes={DIAS}
            selecionados={form.dias_semana}
            onAlternar={alternarDia}
          />

          <CheckboxGrupo
            rotulo="Tipologias"
            opcoes={tipologias.map((t) => ({ valor: String(t.id), rotulo: t.nome }))}
            selecionados={form.tipologia_ids}
            onAlternar={alternarTipologia}
          />

          <TextField
            rotulo="Observação"
            value={form.observacao}
            onChange={(e) => setForm((f) => ({ ...f, observacao: e.target.value }))}
          />

          <label className={styles.opcaoTurno}>
            <input
              type="checkbox"
              checked={form.ativo}
              onChange={(e) => setForm((f) => ({ ...f, ativo: e.target.checked }))}
            />
            Ativo
          </label>

          <div className={styles.acoesForm}>
            <Button variante="secundaria" onClick={fechar} disabled={salvando}>
              Cancelar
            </Button>
            <Button onClick={salvar} carregando={salvando}>
              Salvar
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}

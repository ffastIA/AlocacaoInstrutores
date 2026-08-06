import { useEffect, useState } from "react";
import { api } from "../../../api/cliente";
import { ApiError } from "../../../api/erros";
import type { Projeto, ProjetoIn } from "../../../api/types";
import { Alert } from "../../../components/Alert";
import { Button } from "../../../components/Button";
import { Modal } from "../../../components/Modal";
import { Spinner } from "../../../components/Spinner";
import { Table } from "../../../components/Table";
import type { ColunaTabela } from "../../../components/Table";
import { TextField } from "../../../components/TextField";
import styles from "./ProjetosTab.module.css";

interface FormState {
  nome: string;
  descricao: string;
  ativo: boolean;
}

function formVazio(): FormState {
  return { nome: "", descricao: "", ativo: true };
}

export function ProjetosTab() {
  const [projetos, setProjetos] = useState<Projeto[] | null>(null);
  const [erroCarga, setErroCarga] = useState<string | null>(null);

  const [editando, setEditando] = useState<Projeto | "novo" | null>(null);
  const [form, setForm] = useState<FormState>(formVazio());
  const [erroForm, setErroForm] = useState<string | null>(null);
  const [salvando, setSalvando] = useState(false);

  async function carregar(): Promise<void> {
    try {
      setProjetos(await api.get<Projeto[]>("/projetos"));
    } catch (excecao) {
      setErroCarga(excecao instanceof ApiError ? excecao.message : "Falha ao carregar projetos.");
    }
  }

  useEffect(() => {
    void carregar();
  }, []);

  function abrirNovo(): void {
    setEditando("novo");
    setForm(formVazio());
    setErroForm(null);
  }

  function abrirEdicao(projeto: Projeto): void {
    setEditando(projeto);
    setForm({ nome: projeto.nome, descricao: projeto.descricao ?? "", ativo: projeto.ativo });
    setErroForm(null);
  }

  function fechar(): void {
    setEditando(null);
    setErroForm(null);
  }

  async function salvar(): Promise<void> {
    if (editando === null) return;
    setErroForm(null);

    if (!form.nome.trim()) {
      setErroForm("Informe o nome do projeto.");
      return;
    }

    const dados: ProjetoIn = {
      nome: form.nome.trim(),
      descricao: form.descricao.trim() || null,
      ativo: form.ativo,
    };

    setSalvando(true);
    try {
      if (editando === "novo") {
        await api.post("/projetos", dados);
      } else {
        await api.put(`/projetos/${editando.id}`, dados);
      }
      fechar();
      await carregar();
    } catch (excecao) {
      setErroForm(excecao instanceof ApiError ? excecao.message : "Não foi possível salvar.");
    } finally {
      setSalvando(false);
    }
  }

  if (erroCarga) return <Alert variante="erro">{erroCarga}</Alert>;
  if (projetos === null) return <Spinner rotulo="Carregando projetos…" />;

  const colunas: ColunaTabela<Projeto>[] = [
    {
      chave: "nome",
      titulo: "Nome",
      ordenavel: true,
      valorOrdenacao: (p) => p.nome,
      renderizar: (p) => (
        <button type="button" className={styles.linkNome} onClick={() => abrirEdicao(p)}>
          {p.nome}
        </button>
      ),
    },
    { chave: "descricao", titulo: "Descrição", renderizar: (p) => p.descricao ?? "—" },
    { chave: "instrutores", titulo: "Instrutores", numerica: true, renderizar: (p) => p.total_instrutores },
    { chave: "ativo", titulo: "Ativo", renderizar: (p) => (p.ativo ? "Sim" : "Não") },
  ];

  return (
    <div className={styles.container}>
      <div className={styles.acoesTopo}>
        <Button onClick={abrirNovo}>Novo projeto</Button>
      </div>

      <Table colunas={colunas} linhas={projetos} chaveLinha={(p) => p.id} />

      <Modal
        aberto={editando !== null}
        titulo={editando === "novo" ? "Novo projeto" : "Editar projeto"}
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
          <TextField
            rotulo="Descrição"
            value={form.descricao}
            onChange={(e) => setForm((f) => ({ ...f, descricao: e.target.value }))}
          />
          <label className={styles.opcaoAtivo}>
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

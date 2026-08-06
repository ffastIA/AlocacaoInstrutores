import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api } from "../../api/cliente";
import { ApiError } from "../../api/erros";
import type { Cenario, CenarioIn, PesosObjetivo, Projeto, Simulacao } from "../../api/types";
import { Alert } from "../../components/Alert";
import { Button } from "../../components/Button";
import { DateRangeField } from "../../components/DateRangeField";
import { EmptyState } from "../../components/EmptyState";
import { Modal } from "../../components/Modal";
import { NumberField } from "../../components/NumberField";
import { Spinner } from "../../components/Spinner";
import { Table } from "../../components/Table";
import type { ColunaTabela } from "../../components/Table";
import { TextField } from "../../components/TextField";
import { CheckboxGrupo } from "../dados/cadastros/CheckboxGrupo";
import { PESOS_META } from "./pesos";
import styles from "./CenariosPage.module.css";

interface FormState {
  nome: string;
  descricao: string;
  periodo_de: string;
  periodo_ate: string;
  projeto_ids: string[];
  permitir_compartilhamento: boolean;
  pesos: PesosObjetivo;
}

function formVazio(): FormState {
  return {
    nome: "",
    descricao: "",
    periodo_de: "",
    periodo_ate: "",
    projeto_ids: [],
    permitir_compartilhamento: false,
    pesos: {
      maximizar_aproveitamento: 0.4,
      antecipar_inicio: 0.2,
      balancear_carga_instrutores: 0.2,
      balancear_tipologias: 0.2,
    },
  };
}

function formDeCenario(cenario: Cenario): FormState {
  return {
    nome: cenario.nome,
    descricao: cenario.descricao ?? "",
    periodo_de: cenario.periodo_de,
    periodo_ate: cenario.periodo_ate,
    projeto_ids: cenario.projeto_ids.map(String),
    permitir_compartilhamento: cenario.permitir_compartilhamento,
    pesos: cenario.pesos_objetivo,
  };
}

/** Cenários de simulação: período, escopo, compartilhamento e pesos do objetivo. */
export function CenariosPage() {
  const navegar = useNavigate();
  const [cenarios, setCenarios] = useState<Cenario[] | null>(null);
  const [projetos, setProjetos] = useState<Projeto[]>([]);
  const [erroCarga, setErroCarga] = useState<string | null>(null);

  const [modalAberto, setModalAberto] = useState(false);
  const [editando, setEditando] = useState<Cenario | null>(null);
  const [form, setForm] = useState<FormState>(formVazio());
  const [erroForm, setErroForm] = useState<string | null>(null);
  const [salvando, setSalvando] = useState(false);

  const [executando, setExecutando] = useState<number | null>(null);
  const [erroExecucao, setErroExecucao] = useState<{ cenarioId: number; mensagem: string } | null>(
    null,
  );
  const [duplicando, setDuplicando] = useState<number | null>(null);

  async function carregar(): Promise<void> {
    try {
      const [listaCenarios, listaProjetos] = await Promise.all([
        api.get<Cenario[]>("/cenarios"),
        api.get<Projeto[]>("/projetos"),
      ]);
      setCenarios(listaCenarios);
      setProjetos(listaProjetos);
    } catch (excecao) {
      setErroCarga(excecao instanceof ApiError ? excecao.message : "Falha ao carregar cenários.");
    }
  }

  useEffect(() => {
    void carregar();
  }, []);

  function abrirNovo(): void {
    setEditando(null);
    setForm(formVazio());
    setErroForm(null);
    setModalAberto(true);
  }

  function abrirEdicao(cenario: Cenario): void {
    setEditando(cenario);
    setForm(formDeCenario(cenario));
    setErroForm(null);
    setModalAberto(true);
  }

  function fechar(): void {
    setModalAberto(false);
    setErroForm(null);
  }

  function alternarProjeto(valor: string): void {
    setForm((f) => ({
      ...f,
      projeto_ids: f.projeto_ids.includes(valor)
        ? f.projeto_ids.filter((p) => p !== valor)
        : [...f.projeto_ids, valor],
    }));
  }

  async function salvar(): Promise<void> {
    setErroForm(null);

    if (!form.nome.trim()) {
      setErroForm("Informe o nome do cenário.");
      return;
    }
    if (!form.periodo_de || !form.periodo_ate) {
      setErroForm("Informe o período simulado.");
      return;
    }
    if (form.periodo_ate < form.periodo_de) {
      setErroForm("A data final do período é anterior à data inicial.");
      return;
    }
    const pesos = Object.values(form.pesos);
    if (pesos.some((p) => p < 0)) {
      setErroForm("Os pesos devem ser não negativos.");
      return;
    }
    if (pesos.every((p) => p === 0)) {
      setErroForm("Todos os pesos estão zerados — informe ao menos um critério de otimização.");
      return;
    }

    const dados: CenarioIn = {
      nome: form.nome.trim(),
      descricao: form.descricao.trim() || null,
      periodo_de: form.periodo_de,
      periodo_ate: form.periodo_ate,
      projeto_ids: form.projeto_ids.map(Number),
      permitir_compartilhamento: form.permitir_compartilhamento,
      pesos_objetivo: form.pesos,
    };

    setSalvando(true);
    try {
      if (editando) {
        await api.put(`/cenarios/${editando.id}`, dados);
      } else {
        await api.post("/cenarios", dados);
      }
      fechar();
      await carregar();
    } catch (excecao) {
      setErroForm(excecao instanceof ApiError ? excecao.message : "Não foi possível salvar.");
    } finally {
      setSalvando(false);
    }
  }

  async function duplicar(cenario: Cenario): Promise<void> {
    setDuplicando(cenario.id);
    try {
      await api.post(`/cenarios/${cenario.id}/duplicar`);
      await carregar();
    } catch (excecao) {
      setErroCarga(excecao instanceof ApiError ? excecao.message : "Não foi possível duplicar.");
    } finally {
      setDuplicando(null);
    }
  }

  async function executar(cenario: Cenario): Promise<void> {
    setErroExecucao(null);
    setExecutando(cenario.id);
    try {
      const simulacao = await api.post<Simulacao>("/simulacoes/executar", {
        cenario_id: cenario.id,
      });
      navegar(`/simulacao/oportunidades?simulacao=${simulacao.id}`);
    } catch (excecao) {
      setErroExecucao({
        cenarioId: cenario.id,
        mensagem:
          excecao instanceof ApiError ? excecao.message : "Não foi possível executar a simulação.",
      });
    } finally {
      setExecutando(null);
    }
  }

  if (erroCarga) return <Alert variante="erro">{erroCarga}</Alert>;
  if (cenarios === null) return <Spinner rotulo="Carregando cenários…" />;

  const colunas: ColunaTabela<Cenario>[] = [
    {
      chave: "nome",
      titulo: "Nome",
      ordenavel: true,
      valorOrdenacao: (c) => c.nome,
      renderizar: (c) => (
        <button type="button" className={styles.linkNome} onClick={() => abrirEdicao(c)}>
          {c.nome}
        </button>
      ),
    },
    { chave: "periodo", titulo: "Período", renderizar: (c) => `${c.periodo_de} a ${c.periodo_ate}` },
    {
      chave: "escopo",
      titulo: "Escopo",
      renderizar: (c) =>
        c.projeto_ids.length === 0
          ? "Todos os projetos"
          : c.projeto_ids
              .map((id) => projetos.find((p) => p.id === id)?.nome ?? id)
              .join(", "),
    },
    {
      chave: "pesos",
      titulo: "Pesos",
      renderizar: (c) =>
        PESOS_META.map((p) => `${p.rotulo.split(" ")[0]}: ${c.pesos_objetivo[p.chave]}`).join(
          " · ",
        ),
    },
    {
      chave: "acoes",
      titulo: "",
      renderizar: (c) => (
        <div className={styles.acoesLinha}>
          <Button
            variante="primaria"
            onClick={() => void executar(c)}
            carregando={executando === c.id}
          >
            Executar
          </Button>
          <Button
            variante="secundaria"
            onClick={() => void duplicar(c)}
            carregando={duplicando === c.id}
          >
            Duplicar
          </Button>
        </div>
      ),
    },
  ];

  return (
    <div className={styles.container}>
      <div className={styles.cabecalho}>
        <h1 className={styles.titulo}>Cenários</h1>
        <Button onClick={abrirNovo}>Novo cenário</Button>
      </div>

      {erroExecucao && (
        <Alert variante="erro" titulo="Não foi possível executar">
          {erroExecucao.mensagem}
          {erroExecucao.mensagem.includes("Tipologias pendentes") && (
            <>
              {" "}
              <Link to="/dados/cadastros?aba=tipologias">Configurar tipologias</Link>.
            </>
          )}
          {erroExecucao.mensagem.toLowerCase().includes("instrutor") &&
            !erroExecucao.mensagem.includes("Tipologias pendentes") && (
              <>
                {" "}
                <Link to="/dados/importacao">Importar instrutores</Link>.
              </>
            )}
        </Alert>
      )}

      {cenarios.length === 0 ? (
        <EmptyState
          titulo="Nenhum cenário cadastrado"
          descricao="Crie o primeiro cenário para poder executar uma simulação."
          acao={<Button onClick={abrirNovo}>Novo cenário</Button>}
        />
      ) : (
        <Table colunas={colunas} linhas={cenarios} chaveLinha={(c) => c.id} />
      )}

      <Modal
        aberto={modalAberto}
        titulo={editando ? "Editar cenário" : "Novo cenário"}
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
            rotulo="Descrição (opcional)"
            value={form.descricao}
            onChange={(e) => setForm((f) => ({ ...f, descricao: e.target.value }))}
          />
          <DateRangeField
            rotuloInicio="Período — de"
            rotuloFim="Período — até"
            valorInicio={form.periodo_de}
            valorFim={form.periodo_ate}
            onChangeInicio={(valor) => setForm((f) => ({ ...f, periodo_de: valor }))}
            onChangeFim={(valor) => setForm((f) => ({ ...f, periodo_ate: valor }))}
          />

          <CheckboxGrupo
            rotulo="Projetos no escopo"
            opcoes={projetos.map((p) => ({ valor: String(p.id), rotulo: p.nome }))}
            selecionados={form.projeto_ids}
            onAlternar={alternarProjeto}
          />
          <p className={styles.dica}>Deixe todos desmarcados para simular todos os projetos.</p>

          <label className={styles.opcaoCheckbox}>
            <input
              type="checkbox"
              checked={form.permitir_compartilhamento}
              onChange={(e) =>
                setForm((f) => ({ ...f, permitir_compartilhamento: e.target.checked }))
              }
            />
            Permitir compartilhamento de instrutores entre projetos
          </label>
          <p className={styles.dica}>
            {form.permitir_compartilhamento
              ? "Instrutores de qualquer projeto podem atender turmas de outros projetos no escopo."
              : "Cada instrutor só atende turmas do seu próprio projeto."}
          </p>

          <fieldset className={styles.pesos}>
            <legend className={styles.rotuloGrupo}>Pesos do objetivo</legend>
            {PESOS_META.map((meta) => (
              <div key={meta.chave} className={styles.linhaPeso}>
                <NumberField
                  rotulo={meta.rotulo}
                  value={form.pesos[meta.chave]}
                  min={0}
                  step={0.1}
                  onChange={(valor) =>
                    setForm((f) => ({
                      ...f,
                      pesos: { ...f.pesos, [meta.chave]: valor ?? 0 },
                    }))
                  }
                />
                <p className={styles.descricaoPeso}>{meta.descricao}</p>
              </div>
            ))}
          </fieldset>

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

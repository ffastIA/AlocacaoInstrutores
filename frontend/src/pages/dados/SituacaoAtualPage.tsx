import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../../api/cliente";
import { ApiError } from "../../api/erros";
import type {
  Instrutor,
  Modalidade,
  Tipologia,
  Turno,
  TurmaEmAndamento,
  TurmaEmAndamentoIn,
} from "../../api/types";
import { Alert } from "../../components/Alert";
import { Button } from "../../components/Button";
import { ConfirmDialog } from "../../components/ConfirmDialog";
import { DateField } from "../../components/DateField";
import { EmptyState } from "../../components/EmptyState";
import { Modal } from "../../components/Modal";
import { Select } from "../../components/Select";
import { Spinner } from "../../components/Spinner";
import { Table } from "../../components/Table";
import type { ColunaTabela } from "../../components/Table";
import { TextField } from "../../components/TextField";
import styles from "./SituacaoAtualPage.module.css";

const MODALIDADES: { valor: Modalidade; rotulo: string }[] = [
  { valor: "regular_seg_qua", rotulo: "Regular (segunda e quarta)" },
  { valor: "regular_ter_qui", rotulo: "Regular (terça e quinta)" },
  { valor: "intensiva_seg_qui", rotulo: "Intensiva (segunda a quinta)" },
];

const ROTULO_TURNO: Record<Turno, string> = { manha: "Manhã", tarde: "Tarde", noite: "Noite" };

interface FormState {
  instrutor_id: string;
  tipologia_id: string;
  modalidade: Modalidade;
  turno: string;
  data_inicio: string;
  data_fim_prevista: string;
  codigo_turma: string;
}

function formVazio(): FormState {
  return {
    instrutor_id: "",
    tipologia_id: "",
    modalidade: "regular_seg_qua",
    turno: "",
    data_inicio: "",
    data_fim_prevista: "",
    codigo_turma: "",
  };
}

/** Situação atual das alocações — ponto de partida das simulações. */
export function SituacaoAtualPage() {
  const [turmas, setTurmas] = useState<TurmaEmAndamento[] | null>(null);
  const [instrutores, setInstrutores] = useState<Instrutor[]>([]);
  const [tipologias, setTipologias] = useState<Tipologia[]>([]);
  const [erroCarga, setErroCarga] = useState<string | null>(null);

  const [modalAberto, setModalAberto] = useState(false);
  const [editando, setEditando] = useState<TurmaEmAndamento | null>(null);
  const [form, setForm] = useState<FormState>(formVazio());
  const [erroForm, setErroForm] = useState<string | null>(null);
  const [salvando, setSalvando] = useState(false);

  const [removendo, setRemovendo] = useState<TurmaEmAndamento | null>(null);
  const [confirmandoRemocao, setConfirmandoRemocao] = useState(false);

  async function carregar(): Promise<void> {
    try {
      const [listaTurmas, listaInstrutores, listaTipologias] = await Promise.all([
        api.get<TurmaEmAndamento[]>("/turmas-em-andamento"),
        api.get<Instrutor[]>("/instrutores"),
        api.get<Tipologia[]>("/tipologias"),
      ]);
      setTurmas(listaTurmas);
      setInstrutores(listaInstrutores);
      setTipologias(listaTipologias);
    } catch (excecao) {
      setErroCarga(
        excecao instanceof ApiError ? excecao.message : "Falha ao carregar a situação atual.",
      );
    }
  }

  useEffect(() => {
    void carregar();
  }, []);

  const instrutorSelecionado = instrutores.find((i) => String(i.id) === form.instrutor_id);
  const turnosDoInstrutor = instrutorSelecionado?.turnos ?? [];

  function abrirNova(): void {
    setEditando(null);
    setForm(formVazio());
    setErroForm(null);
    setModalAberto(true);
  }

  function abrirEdicao(turma: TurmaEmAndamento): void {
    setEditando(turma);
    setForm({
      instrutor_id: String(turma.instrutor_id),
      tipologia_id: String(turma.tipologia_id),
      modalidade: turma.modalidade,
      turno: turma.turno,
      data_inicio: turma.data_inicio,
      data_fim_prevista: turma.data_fim_prevista,
      codigo_turma: turma.codigo_turma ?? "",
    });
    setErroForm(null);
    setModalAberto(true);
  }

  function fechar(): void {
    setModalAberto(false);
    setEditando(null);
    setErroForm(null);
  }

  async function salvar(): Promise<void> {
    setErroForm(null);

    if (!form.instrutor_id || !form.tipologia_id || !form.turno) {
      setErroForm("Preencha instrutor, tipologia e turno.");
      return;
    }
    if (!form.data_inicio || !form.data_fim_prevista) {
      setErroForm("Preencha as datas de início e término prevista.");
      return;
    }
    if (form.data_fim_prevista < form.data_inicio) {
      setErroForm("A data de término prevista é anterior à data de início.");
      return;
    }

    const dados: TurmaEmAndamentoIn = {
      instrutor_id: Number(form.instrutor_id),
      tipologia_id: Number(form.tipologia_id),
      modalidade: form.modalidade,
      turno: form.turno as Turno,
      data_inicio: form.data_inicio,
      data_fim_prevista: form.data_fim_prevista,
      codigo_turma: form.codigo_turma.trim() || null,
    };

    setSalvando(true);
    try {
      // Não há endpoint de atualização — editar cria o novo registro e só
      // remove o anterior após o sucesso, evitando perda de dados se a nova
      // combinação for rejeitada.
      await api.post("/turmas-em-andamento", dados);
      if (editando) {
        await api.delete(`/turmas-em-andamento/${editando.id}`);
      }
      fechar();
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
      await api.delete(`/turmas-em-andamento/${removendo.id}`);
      setRemovendo(null);
      await carregar();
    } catch (excecao) {
      setErroCarga(excecao instanceof ApiError ? excecao.message : "Não foi possível remover.");
    } finally {
      setConfirmandoRemocao(false);
    }
  }

  const instrutoresSobrecarregados = useMemo(() => {
    if (!turmas) return [];
    const somaPorChave = new Map<string, number>();
    for (const turma of turmas) {
      const tipologia = tipologias.find((t) => t.id === turma.tipologia_id);
      if (!tipologia?.horas_por_encontro) continue;
      const chave = `${turma.instrutor_id}::${turma.turno}`;
      somaPorChave.set(chave, (somaPorChave.get(chave) ?? 0) + tipologia.horas_por_encontro);
    }
    const alertas: string[] = [];
    for (const [chave, horas] of somaPorChave) {
      const [instrutorId, turno] = chave.split("::");
      const instrutor = instrutores.find((i) => String(i.id) === instrutorId);
      const capacidade = instrutor?.turnos.find((t) => t.turno === turno)?.carga_horaria_horas;
      if (instrutor && capacidade !== undefined && horas > capacidade) {
        alertas.push(
          `${instrutor.nome} — turno ${ROTULO_TURNO[turno as Turno]}: ${horas}h alocadas acima da capacidade declarada (${capacidade}h)`,
        );
      }
    }
    return alertas;
  }, [turmas, tipologias, instrutores]);

  if (erroCarga) return <Alert variante="erro">{erroCarga}</Alert>;
  if (turmas === null) return <Spinner rotulo="Carregando situação atual…" />;

  const colunas: ColunaTabela<TurmaEmAndamento>[] = [
    {
      chave: "instrutor",
      titulo: "Instrutor",
      renderizar: (t) => (
        <button type="button" className={styles.linkNome} onClick={() => abrirEdicao(t)}>
          {t.instrutor_nome}
        </button>
      ),
    },
    { chave: "tipologia", titulo: "Tipologia", renderizar: (t) => t.tipologia_nome },
    {
      chave: "modalidade",
      titulo: "Modalidade",
      renderizar: (t) => MODALIDADES.find((m) => m.valor === t.modalidade)?.rotulo ?? t.modalidade,
    },
    { chave: "turno", titulo: "Turno", renderizar: (t) => ROTULO_TURNO[t.turno] },
    {
      chave: "data_inicio",
      titulo: "Início",
      ordenavel: true,
      valorOrdenacao: (t) => t.data_inicio,
      renderizar: (t) => t.data_inicio,
    },
    {
      chave: "data_fim",
      titulo: "Término previsto",
      ordenavel: true,
      valorOrdenacao: (t) => t.data_fim_prevista,
      renderizar: (t) => t.data_fim_prevista,
    },
    {
      chave: "acoes",
      titulo: "",
      renderizar: (t) => (
        <button type="button" className={styles.linkRemover} onClick={() => setRemovendo(t)}>
          Remover
        </button>
      ),
    },
  ];

  return (
    <div className={styles.container}>
      <div className={styles.cabecalho}>
        <h1 className={styles.titulo}>Situação Atual</h1>
        <Button onClick={abrirNova}>Nova turma em andamento</Button>
      </div>
      <p className={styles.descricao}>
        Turmas em execução, ordenadas pela data de término prevista — evidenciando quais
        instrutores liberam capacidade primeiro.
      </p>

      {instrutoresSobrecarregados.length > 0 && (
        <Alert variante="alerta" titulo="Capacidade declarada excedida">
          <ul>
            {instrutoresSobrecarregados.map((linha) => (
              <li key={linha}>{linha}</li>
            ))}
          </ul>
        </Alert>
      )}

      {turmas.length === 0 ? (
        <EmptyState
          titulo="Nenhuma turma em andamento"
          descricao="A simulação partirá com todos os instrutores livres."
          acao={<Link to="/dados/importacao">Importar planilha de turmas</Link>}
        />
      ) : (
        <Table colunas={colunas} linhas={turmas} chaveLinha={(t) => t.id} />
      )}

      <Modal
        aberto={modalAberto}
        titulo={editando ? "Editar turma em andamento" : "Nova turma em andamento"}
        onFechar={fechar}
      >
        {erroForm && (
          <Alert variante="erro" titulo="Não foi possível salvar">
            {erroForm}
          </Alert>
        )}
        <div className={styles.form}>
          <Select
            rotulo="Instrutor"
            opcoes={[
              { valor: "", rotulo: "Selecione…" },
              ...instrutores.map((i) => ({ valor: String(i.id), rotulo: i.nome })),
            ]}
            value={form.instrutor_id}
            onChange={(e) => setForm((f) => ({ ...f, instrutor_id: e.target.value, turno: "" }))}
          />
          <Select
            rotulo="Tipologia"
            opcoes={[
              { valor: "", rotulo: "Selecione…" },
              ...tipologias.map((t) => ({ valor: String(t.id), rotulo: t.nome })),
            ]}
            value={form.tipologia_id}
            onChange={(e) => setForm((f) => ({ ...f, tipologia_id: e.target.value }))}
          />
          <Select
            rotulo="Modalidade"
            opcoes={MODALIDADES.map((m) => ({ valor: m.valor, rotulo: m.rotulo }))}
            value={form.modalidade}
            onChange={(e) => setForm((f) => ({ ...f, modalidade: e.target.value as Modalidade }))}
          />
          <Select
            rotulo="Turno"
            opcoes={[
              { valor: "", rotulo: instrutorSelecionado ? "Selecione…" : "Selecione o instrutor primeiro" },
              ...turnosDoInstrutor.map((t) => ({
                valor: t.turno,
                rotulo: `${ROTULO_TURNO[t.turno]} (${t.carga_horaria_horas}h)`,
              })),
            ]}
            value={form.turno}
            disabled={!instrutorSelecionado}
            onChange={(e) => setForm((f) => ({ ...f, turno: e.target.value }))}
          />
          <DateField
            rotulo="Data de início"
            value={form.data_inicio}
            onChange={(e) => setForm((f) => ({ ...f, data_inicio: e.target.value }))}
          />
          <DateField
            rotulo="Data de término prevista"
            value={form.data_fim_prevista}
            min={form.data_inicio || undefined}
            onChange={(e) => setForm((f) => ({ ...f, data_fim_prevista: e.target.value }))}
          />
          <TextField
            rotulo="Código da turma (opcional)"
            value={form.codigo_turma}
            onChange={(e) => setForm((f) => ({ ...f, codigo_turma: e.target.value }))}
          />
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

      <ConfirmDialog
        aberto={removendo !== null}
        titulo="Remover turma em andamento"
        mensagem={
          removendo
            ? `Remover a turma de ${removendo.tipologia_nome} de ${removendo.instrutor_nome}?`
            : ""
        }
        confirmando={confirmandoRemocao}
        onConfirmar={confirmarRemocao}
        onCancelar={() => setRemovendo(null)}
      />
    </div>
  );
}

/**
 * Tipos correspondentes aos contratos do backend (FastAPI/Pydantic).
 *
 * Os nomes dos campos seguem exatamente o formato retornado pela API
 * (snake_case) — nenhuma transformação de caso é feita na fronteira, para
 * que uma divergência de contrato apareça como erro de tipo aqui, não como
 * bug silencioso em runtime.
 */

export type Turno = "manha" | "tarde" | "noite";

export type Modalidade = "regular_seg_qua" | "regular_ter_qui" | "intensiva_seg_qui";

export type StatusSimulacao = "pendente" | "executando" | "concluida" | "erro";

export type TipoDataNaoLetiva = "feriado" | "recesso" | "ferias";

// --------------------------------------------------------------------------
// Importação
// --------------------------------------------------------------------------

export interface ErroLinha {
  linha: number;
  motivo: string;
  coluna: string | null;
}

export interface AlertaImportacao {
  linha: number | null;
  mensagem: string;
}

export interface ResultadoImportacao {
  sucesso: boolean;
  importados: number;
  atualizados: number;
  rejeitados: number;
  erro_arquivo: string | null;
  erros: ErroLinha[];
  alertas: AlertaImportacao[];
}

// --------------------------------------------------------------------------
// Cadastros
// --------------------------------------------------------------------------

export interface Projeto {
  id: number;
  nome: string;
  descricao: string | null;
  ativo: boolean;
  total_instrutores: number;
}

export interface Tipologia {
  id: number;
  nome: string;
  carga_horaria_total_horas: number | null;
  horas_por_encontro: number | null;
  descricao: string | null;
  configurada: boolean;
  num_encontros: number | null;
  total_instrutores: number;
}

export interface TipologiaPendente {
  id: number;
  nome: string;
  total_instrutores: number;
}

export interface TurnoDisponivel {
  turno: Turno;
  carga_horaria_horas: number;
}

export interface Instrutor {
  id: number;
  nome: string;
  projeto_id: number;
  projeto_nome: string;
  turnos: TurnoDisponivel[];
  dias_semana: number[];
  tipologias: string[];
  observacao: string | null;
  ativo: boolean;
}

export interface TurmaEmAndamento {
  id: number;
  codigo_turma: string | null;
  instrutor_id: number;
  instrutor_nome: string;
  tipologia_id: number;
  tipologia_nome: string;
  projeto_id: number;
  modalidade: Modalidade;
  turno: Turno;
  data_inicio: string;
  data_fim_prevista: string;
}

// --------------------------------------------------------------------------
// Cenários
// --------------------------------------------------------------------------

export interface PesosObjetivo {
  maximizar_aproveitamento: number;
  antecipar_inicio: number;
  balancear_carga_instrutores: number;
  balancear_tipologias: number;
}

export interface Cenario {
  id: number;
  nome: string;
  descricao: string | null;
  periodo_de: string;
  periodo_ate: string;
  projeto_ids: number[];
  permitir_compartilhamento: boolean;
  pesos_objetivo: PesosObjetivo;
  criado_em: string;
}

// --------------------------------------------------------------------------
// Simulações
// --------------------------------------------------------------------------

export interface Simulacao {
  id: number;
  cenario_id: number;
  status: StatusSimulacao;
  iniciado_em: string;
  concluido_em: string | null;
  tempo_execucao_seg: number | null;
  solver_status: string | null;
  objetivo_valor: number | null;
  mensagem_erro: string | null;
}

export interface Encontro {
  data: string;
  turno: Turno;
  horas: number;
}

export interface TurmaSugerida {
  id: number;
  tipologia_id: number;
  tipologia_nome: string;
  instrutor_id: number;
  instrutor_nome: string;
  projeto_id: number;
  modalidade: Modalidade;
  turno: Turno;
  semana_inicio: number;
  data_inicio: string;
  data_fim: string;
  num_encontros: number;
  carga_horaria_total: number;
  encontros: Encontro[];
}

export interface Kpis {
  total_turmas_sugeridas: number;
  horas_formacao_total: number;
  horas_disponiveis_total: number;
  pct_ociosidade: number;
  indice_balanceamento_carga: number;
  indice_balanceamento_tipologia: number;
  horas_reposicao_sexta: number;
}

export interface Oportunidade {
  tipologia_id: number;
  tipologia_nome: string;
  data_inicio: string;
  total_turmas: number;
  instrutor_ids: number[];
}

export interface AgendaItem {
  origem: "em_andamento" | "sugerida";
  tipologia_id: number;
  tipologia_nome: string;
  modalidade: Modalidade;
  turno: Turno;
  data_inicio: string;
  data_fim: string;
}

export interface ComparacaoItem {
  simulacao_id: number;
  cenario_id: number;
  cenario_nome: string;
  periodo_de: string;
  periodo_ate: string;
  permitir_compartilhamento: boolean;
  pesos_objetivo: Record<string, number>;
  kpis: Kpis;
}

export interface Comparacao {
  itens: ComparacaoItem[];
  periodos_divergentes: boolean;
}

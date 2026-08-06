/**
 * Tratamento centralizado de erros da API.
 *
 * O backend retorna `{"detail": "mensagem em português"}` para erros de
 * negócio — essa mensagem já é destinada ao operador e é exibida como está,
 * sem expor detalhes técnicos da resposta HTTP.
 */

export type TipoErroApi = "validacao" | "nao_encontrado" | "servidor_indisponivel" | "desconhecido";

export class ApiError extends Error {
  readonly tipo: TipoErroApi;
  readonly status: number | null;

  constructor(mensagem: string, tipo: TipoErroApi, status: number | null) {
    super(mensagem);
    this.name = "ApiError";
    this.tipo = tipo;
    this.status = status;
  }
}

interface CorpoErroFastApi {
  detail?: string | Array<{ msg?: string; loc?: unknown[] }>;
}

/** Traduz uma resposta HTTP malsucedida em um `ApiError` com mensagem ao usuário. */
export async function converterRespostaEmErro(resposta: Response): Promise<ApiError> {
  const tipo = tipoDoStatus(resposta.status);

  let corpo: CorpoErroFastApi | null = null;
  try {
    corpo = (await resposta.json()) as CorpoErroFastApi;
  } catch {
    // Corpo não é JSON (ex.: erro 502 de um proxy) — segue sem detalhe.
  }

  const mensagem = extrairMensagem(corpo) ?? mensagemPadrao(tipo, resposta.status);
  return new ApiError(mensagem, tipo, resposta.status);
}

/** Erro de rede (backend fora do ar, sem resposta HTTP alguma). */
export function erroDeConexao(): ApiError {
  return new ApiError(
    "Não foi possível conectar ao servidor. Verifique sua conexão e tente novamente.",
    "servidor_indisponivel",
    null,
  );
}

function tipoDoStatus(status: number): TipoErroApi {
  if (status === 404) return "nao_encontrado";
  if (status === 422 || status === 400) return "validacao";
  if (status >= 500) return "servidor_indisponivel";
  return "desconhecido";
}

function extrairMensagem(corpo: CorpoErroFastApi | null): string | null {
  if (!corpo?.detail) return null;
  if (typeof corpo.detail === "string") return corpo.detail;
  // Formato de erro de validação do Pydantic: lista de {msg, loc}.
  const primeira = corpo.detail[0];
  return primeira?.msg ?? null;
}

function mensagemPadrao(tipo: TipoErroApi, status: number): string {
  switch (tipo) {
    case "nao_encontrado":
      return "O recurso solicitado não foi encontrado.";
    case "validacao":
      return "Os dados enviados não puderam ser processados.";
    case "servidor_indisponivel":
      return "O servidor encontrou um problema ao processar a solicitação.";
    default:
      return `A solicitação falhou (código ${status}).`;
  }
}

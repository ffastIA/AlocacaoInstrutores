import { ApiError, converterRespostaEmErro, erroDeConexao } from "./erros";

/**
 * URL base da API, configurável por variável de ambiente — nenhuma alteração
 * de código é necessária para apontar a aplicação a outro ambiente.
 */
export const URL_BASE_API: string =
  (import.meta.env.VITE_API_BASE_URL as string | undefined) ?? "http://localhost:8000";

async function requisitar<T>(caminho: string, opcoes: RequestInit = {}): Promise<T> {
  let resposta: Response;
  try {
    resposta = await fetch(`${URL_BASE_API}${caminho}`, {
      ...opcoes,
      headers: {
        Accept: "application/json",
        ...opcoes.headers,
      },
    });
  } catch {
    throw erroDeConexao();
  }

  if (!resposta.ok) {
    throw await converterRespostaEmErro(resposta);
  }

  if (resposta.status === 204) {
    return undefined as T;
  }

  return (await resposta.json()) as T;
}

function corpoJson(dados: unknown): RequestInit {
  return {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(dados),
  };
}

export const api = {
  get: <T>(caminho: string): Promise<T> => requisitar<T>(caminho),

  post: <T>(caminho: string, dados?: unknown): Promise<T> =>
    requisitar<T>(caminho, dados !== undefined ? corpoJson(dados) : { method: "POST" }),

  put: <T>(caminho: string, dados: unknown): Promise<T> =>
    requisitar<T>(caminho, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(dados),
    }),

  delete: (caminho: string): Promise<void> => requisitar<void>(caminho, { method: "DELETE" }),

  /** Baixa um arquivo (ex.: exportação ou modelo de planilha) como Blob. */
  baixarArquivo: async (caminho: string): Promise<{ blob: Blob; nomeArquivo: string | null }> => {
    let resposta: Response;
    try {
      resposta = await fetch(`${URL_BASE_API}${caminho}`);
    } catch {
      throw erroDeConexao();
    }
    if (!resposta.ok) {
      throw await converterRespostaEmErro(resposta);
    }
    const disposicao = resposta.headers.get("content-disposition");
    const nomeArquivo = disposicao?.match(/filename="?([^"]+)"?/)?.[1] ?? null;
    return { blob: await resposta.blob(), nomeArquivo };
  },
};

export { ApiError };

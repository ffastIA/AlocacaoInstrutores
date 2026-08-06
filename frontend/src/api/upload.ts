import { URL_BASE_API } from "./cliente";
import { ApiError, erroDeConexao } from "./erros";

/**
 * Envia um arquivo com acompanhamento de progresso.
 *
 * `fetch` não expõe progresso de upload — por isso este módulo usa
 * `XMLHttpRequest` só aqui, mantendo o restante do cliente em `fetch`.
 */
export function enviarArquivo<T>(
  caminho: string,
  arquivo: File,
  onProgresso?: (percentual: number) => void,
): Promise<T> {
  return new Promise((resolve, reject) => {
    const formData = new FormData();
    formData.append("arquivo", arquivo);

    const xhr = new XMLHttpRequest();
    xhr.open("POST", `${URL_BASE_API}${caminho}`);
    xhr.responseType = "json";

    xhr.upload.addEventListener("progress", (evento) => {
      if (evento.lengthComputable && onProgresso) {
        onProgresso(Math.round((evento.loaded / evento.total) * 100));
      }
    });

    xhr.addEventListener("load", () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        resolve(xhr.response as T);
        return;
      }
      const corpo = xhr.response as { detail?: string } | null;
      reject(
        new ApiError(
          corpo?.detail ?? "Não foi possível processar o arquivo enviado.",
          xhr.status === 422 || xhr.status === 400 ? "validacao" : "desconhecido",
          xhr.status,
        ),
      );
    });

    xhr.addEventListener("error", () => reject(erroDeConexao()));
    xhr.addEventListener("abort", () => reject(erroDeConexao()));

    xhr.send(formData);
  });
}

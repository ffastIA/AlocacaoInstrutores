import { useRef, useState } from "react";
import type { ReactNode } from "react";
import { api } from "../api/cliente";
import { ApiError } from "../api/erros";
import { enviarArquivo } from "../api/upload";
import type { ResultadoImportacao } from "../api/types";
import { Alert } from "./Alert";
import { Button } from "./Button";
import { Card } from "./Card";
import styles from "./ImportSection.module.css";

const EXTENSOES_ACEITAS = [".xlsx", ".csv"];
const MAX_ERROS_VISIVEIS = 10;

interface ImportSectionProps {
  titulo: string;
  tipo: string;
  orientacoes: ReactNode;
  onResultado?: (resultado: ResultadoImportacao) => void;
}

/** Seção de upload de uma planilha: seleção, modelo, envio e relatório. */
export function ImportSection({ titulo, tipo, orientacoes, onResultado }: ImportSectionProps) {
  const refInput = useRef<HTMLInputElement>(null);
  const [arquivo, setArquivo] = useState<File | null>(null);
  const [erroFormato, setErroFormato] = useState<string | null>(null);
  const [enviando, setEnviando] = useState(false);
  const [progresso, setProgresso] = useState(0);
  const [resultado, setResultado] = useState<ResultadoImportacao | null>(null);
  const [erroEnvio, setErroEnvio] = useState<string | null>(null);
  const [mostrarTodosErros, setMostrarTodosErros] = useState(false);
  const [baixandoModelo, setBaixandoModelo] = useState(false);

  function selecionarArquivo(evento: React.ChangeEvent<HTMLInputElement>): void {
    const selecionado = evento.target.files?.[0] ?? null;
    setResultado(null);
    setErroEnvio(null);
    setMostrarTodosErros(false);

    if (!selecionado) {
      setArquivo(null);
      setErroFormato(null);
      return;
    }

    const extensaoValida = EXTENSOES_ACEITAS.some((ext) =>
      selecionado.name.toLowerCase().endsWith(ext),
    );
    if (!extensaoValida) {
      setArquivo(null);
      setErroFormato(
        `Formato não suportado. Envie um arquivo ${EXTENSOES_ACEITAS.join(" ou ")}.`,
      );
      return;
    }

    setErroFormato(null);
    setArquivo(selecionado);
  }

  async function enviar(): Promise<void> {
    if (!arquivo) return;
    setEnviando(true);
    setProgresso(0);
    setErroEnvio(null);
    setResultado(null);

    try {
      const resposta = await enviarArquivo<ResultadoImportacao>(
        `/importar/${tipo}`,
        arquivo,
        setProgresso,
      );
      setResultado(resposta);
      onResultado?.(resposta);
      setArquivo(null);
      if (refInput.current) refInput.current.value = "";
    } catch (excecao) {
      setErroEnvio(
        excecao instanceof ApiError
          ? excecao.message
          : "Não foi possível enviar o arquivo. Tente novamente.",
      );
    } finally {
      setEnviando(false);
    }
  }

  async function baixarModelo(): Promise<void> {
    setBaixandoModelo(true);
    try {
      const { blob, nomeArquivo } = await api.baixarArquivo(`/importar/modelos/${tipo}`);
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = nomeArquivo ?? `modelo_${tipo}.xlsx`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(url);
    } catch {
      setErroEnvio("Não foi possível baixar o modelo. Tente novamente.");
    } finally {
      setBaixandoModelo(false);
    }
  }

  const errosVisiveis =
    resultado && !mostrarTodosErros ? resultado.erros.slice(0, MAX_ERROS_VISIVEIS) : resultado?.erros;
  const errosOcultos = resultado ? resultado.erros.length - MAX_ERROS_VISIVEIS : 0;

  return (
    <Card
      titulo={titulo}
      acoes={
        <Button variante="secundaria" onClick={baixarModelo} carregando={baixandoModelo}>
          Baixar modelo
        </Button>
      }
    >
      <div className={styles.orientacoes}>{orientacoes}</div>

      <div className={styles.envio}>
        <input
          ref={refInput}
          type="file"
          accept=".xlsx,.csv"
          onChange={selecionarArquivo}
          disabled={enviando}
          aria-label={`Selecionar planilha de ${titulo.toLowerCase()}`}
        />
        <Button onClick={enviar} disabled={!arquivo} carregando={enviando}>
          Enviar
        </Button>
      </div>

      {erroFormato && (
        <p className={styles.erroFormato} role="alert">
          {erroFormato}
        </p>
      )}

      {enviando && (
        <div className={styles.progresso} role="progressbar" aria-valuenow={progresso}>
          <div className={styles.progressoBarra} style={{ width: `${progresso}%` }} />
        </div>
      )}

      {erroEnvio && (
        <Alert variante="erro" titulo="Falha no envio">
          {erroEnvio}
        </Alert>
      )}

      {resultado && (
        <div className={styles.relatorio}>
          {resultado.erro_arquivo ? (
            <Alert variante="erro" titulo="Arquivo recusado">
              {resultado.erro_arquivo} Baixe o modelo acima e confira as colunas esperadas.
            </Alert>
          ) : (
            <>
              <Alert variante={resultado.rejeitados > 0 ? "alerta" : "sucesso"} titulo="Importação concluída">
                {resultado.importados} registro(s) importado(s)
                {resultado.atualizados > 0 && `, ${resultado.atualizados} atualizado(s)`}
                {resultado.rejeitados > 0 && `, ${resultado.rejeitados} rejeitado(s)`}.
              </Alert>

              {resultado.erros.length > 0 && (
                <div className={styles.listaErros}>
                  <p className={styles.tituloLista}>Linhas rejeitadas</p>
                  <ul>
                    {errosVisiveis?.map((erro, indice) => (
                      <li key={`${erro.linha}-${indice}`}>
                        Linha {erro.linha}
                        {erro.coluna && ` (${erro.coluna})`}: {erro.motivo}
                      </li>
                    ))}
                  </ul>
                  {errosOcultos > 0 && !mostrarTodosErros && (
                    <button
                      type="button"
                      className={styles.botaoExpandir}
                      onClick={() => setMostrarTodosErros(true)}
                    >
                      Mostrar mais {errosOcultos} linha(s)
                    </button>
                  )}
                </div>
              )}

              {resultado.alertas.length > 0 && (
                <Alert variante="alerta" titulo="Avisos">
                  <ul>
                    {resultado.alertas.map((alerta, indice) => (
                      <li key={indice}>
                        {alerta.linha !== null && `Linha ${alerta.linha}: `}
                        {alerta.mensagem}
                      </li>
                    ))}
                  </ul>
                </Alert>
              )}
            </>
          )}
        </div>
      )}
    </Card>
  );
}

import { useState } from "react";
import { Link } from "react-router-dom";
import { Alert } from "../../components/Alert";
import { ImportSection } from "../../components/ImportSection";
import { api } from "../../api/cliente";
import type { TipologiaPendente } from "../../api/types";
import styles from "./ImportacaoPage.module.css";

/** Upload das quatro planilhas de entrada, com relatório de validação por linha. */
export function ImportacaoPage() {
  const [pendentes, setPendentes] = useState<TipologiaPendente[] | null>(null);

  async function aoImportarInstrutores(): Promise<void> {
    try {
      const lista = await api.get<TipologiaPendente[]>("/tipologias/pendentes");
      setPendentes(lista.length > 0 ? lista : null);
    } catch {
      // A importação já foi confirmada; a checagem de pendências é só um reforço.
    }
  }

  return (
    <div className={styles.container}>
      <h1 className={styles.titulo}>Importação de Dados</h1>
      <p className={styles.descricao}>
        Envie as planilhas de instrutores, tipologias, turmas em andamento e datas não
        letivas. Campos com múltiplos valores usam ponto e vírgula como separador, ex.:{" "}
        <code>manha;tarde</code>.
      </p>

      {pendentes && (
        <Alert variante="alerta" titulo="Tipologias pendentes de configuração">
          {pendentes.length} tipologia(s) nova(s) ainda sem carga horária configurada:{" "}
          {pendentes.map((t) => t.nome).join(", ")}. A simulação fica bloqueada até que
          sejam configuradas.{" "}
          <Link to="/dados/cadastros?aba=tipologias">Configurar agora</Link>.
        </Alert>
      )}

      <div className={styles.secoes}>
        <ImportSection
          titulo="Instrutores"
          tipo="instrutores"
          onResultado={aoImportarInstrutores}
          orientacoes={
            <>
              Colunas: <code>nome</code>, <code>projeto</code>, <code>turnos</code> (ex.:{" "}
              <code>manha;tarde</code>), <code>carga_horaria_turno</code> (ex.: <code>4;4</code>
              , na mesma ordem de turnos), <code>dias_semana</code> (2=segunda a 6=sexta, ex.:{" "}
              <code>2;3;4;5</code>), <code>tipologias</code> (ex.:{" "}
              <code>Programação;Pixel Art</code>) e <code>observacao</code> (opcional).
              <ul>
                <li>Tipologias e projetos citados e ainda não cadastrados são criados automaticamente.</li>
                <li>Sexta-feira (dia 6) conta apenas como capacidade de reposição.</li>
              </ul>
            </>
          }
        />

        <ImportSection
          titulo="Tipologias"
          tipo="tipologias"
          orientacoes={
            <>
              Colunas: <code>tipologia</code> (nome já usado na planilha de instrutores),{" "}
              <code>carga_horaria_total</code> (24 a 60h), <code>horas_por_encontro</code> e{" "}
              <code>descricao</code> (opcional).
              <ul>
                <li>A carga total precisa ser múltiplo exato das horas por encontro.</li>
              </ul>
            </>
          }
        />

        <ImportSection
          titulo="Turmas em andamento"
          tipo="turmas-em-andamento"
          orientacoes={
            <>
              Colunas: <code>instrutor</code>, <code>tipologia</code>, <code>modalidade</code>{" "}
              (<code>regular_seg_qua</code>, <code>regular_ter_qui</code> ou{" "}
              <code>intensiva_seg_qui</code>), <code>turno</code>, <code>data_inicio</code>,{" "}
              <code>data_fim_prevista</code> (DD/MM/AAAA) e <code>codigo_turma</code>{" "}
              (opcional).
              <ul>
                <li>Deixe a planilha sem linhas se nenhuma turma estiver em curso.</li>
              </ul>
            </>
          }
        />

        <ImportSection
          titulo="Datas não letivas"
          tipo="datas-nao-letivas"
          orientacoes={
            <>
              Colunas: <code>data_inicio</code>, <code>data_fim</code> (opcional, vazio =
              um único dia), <code>descricao</code>, <code>tipo</code> (
              <code>feriado</code>, <code>recesso</code> ou <code>ferias</code>) e{" "}
              <code>projeto</code> (opcional, vazio aplica a todos).
              <ul>
                <li>Estes dados ainda não afetam o cálculo das simulações nesta versão.</li>
              </ul>
            </>
          }
        />
      </div>
    </div>
  );
}

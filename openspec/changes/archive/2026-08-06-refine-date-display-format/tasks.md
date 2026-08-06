## 1. Utilitário compartilhado

- [x] 1.1 Criar `frontend/src/utils/data.ts` com `formatarData(iso: string | null | undefined): string` (dd/mm/aaaa, via manipulação de string — sem construir `Date` a partir de data pura, para não sofrer o off-by-one de fuso horário) e `formatarDataHora(iso: string | null | undefined): string` (dd/mm/aaaa hh:mm); ambas retornam `"—"` para `null`/`undefined`

## 2. Mapa de Oportunidades

- [x] 2.1 `pages/simulacao/resultado/MapaOportunidades.tsx` — célula `data_inicio` da tabela (linha 278), título do Modal de detalhe (linha 327), intervalo `data_inicio`/`data_fim` no detalhe da turma (linha 344)
- [x] 2.2 `pages/simulacao/resultado/LinhaDoTempoOportunidades.tsx` — remover a função local `formatarData` (linhas 19-21) e importar do utilitário compartilhado

## 3. Agenda por Instrutor

- [x] 3.1 `pages/simulacao/AgendaPage.tsx` — coluna "Primeira data livre" da tabela consolidada (linhas 121-126), texto "livre a partir de..." no resumo individual (linhas 199-201), intervalo `data_inicio`/`data_fim` na lista de agenda (linha 222)

## 4. Painel de Indicadores

- [x] 4.1 `pages/simulacao/resultado/PainelIndicadores.tsx` — coluna "Primeira data livre" (linhas 97-101) e data/hora de execução (linha 110, usar `formatarDataHora` no lugar de `.slice(0, 16).replace("T", " ")`)

## 5. Cenários

- [x] 5.1 `pages/simulacao/CenariosPage.tsx` — coluna "Período" da tabela (linha 221)

## 6. Comparação e Histórico

- [x] 6.1 `pages/simulacao/ComparacaoPage.tsx` — linha "Período" da tabela de comparação (linha 19) e data de execução no rótulo do checkbox de seleção (linha 137)
- [x] 6.2 `pages/simulacao/HistoricoPage.tsx` — coluna "Executada em" (linhas 88-94)
- [x] 6.3 `pages/simulacao/SeletorSimulacao.tsx` — data de execução no rótulo de `<option>` (linha 56)

## 7. Dados

- [x] 7.1 `pages/dados/SituacaoAtualPage.tsx` — colunas "Início" e "Término previsto" (linhas 208-214, 215-221)
- [x] 7.2 `pages/dados/DatasNaoLetivasPage.tsx` — coluna "Intervalo" (linhas 191-199), preservando o caso de dia único (`data_inicio === data_fim`) sem repetir a data

## 8. Verificação

- [x] 8.1 Confirmar que nenhum `valorOrdenacao` de coluna foi alterado — ordenação continua sobre a string ISO original
- [x] 8.2 Confirmar que `DateField`/`DateRangeField` (inputs) permanecem em ISO, não tocados
- [x] 8.3 `npm run build` e `npm run lint` no frontend, limpos
- [x] 8.4 Verificação visual ao vivo (frontend + backend rodando): Cenários, Mapa de Oportunidades (tabela e linha do tempo), Agenda, Painel de Indicadores, Comparação, Histórico, Situação Atual, Datas Não Letivas — todas as datas em dd/mm/aaaa (ou dd/mm/aaaa hh:mm onde há hora)

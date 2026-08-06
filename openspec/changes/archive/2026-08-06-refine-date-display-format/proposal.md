## Why

Toda data vinda da API (formato ISO `YYYY-MM-DD`/`YYYY-MM-DDTHH:mm:ss`) é hoje exibida crua nas telas, no formato americano (ex.: "2026-08-06"). Isso é inconsistente com a convenção brasileira (dd/mm/aaaa) usada no resto do produto e obriga o usuário a reler a data mentalmente. Não há nenhuma mudança de comportamento por trás disso — só a forma de leitura da mesma informação.

## What Changes

- Todas as datas exibidas como texto na interface (tabelas, títulos de modal, rótulos, mensagens) passam a aparecer no formato dd/mm/aaaa; datas com hora passam a aparecer como dd/mm/aaaa hh:mm.
- Extração de um utilitário compartilhado de formatação de data (`frontend/src/utils/data.ts`), substituindo a função local hoje duplicada apenas dentro de `LinhaDoTempoOportunidades.tsx` e as manipulações ad-hoc de string (`.slice(0, 16).replace("T", " ")`) espalhadas em várias telas.
- Os campos `<input type="date">` (`DateField`/`DateRangeField`) continuam em ISO — é o formato nativo do HTML e não é uma leitura de texto pelo usuário. Ordenação de colunas por data continua comparando strings ISO (ordenação lexicográfica é equivalente).
- Nenhuma mudança de API, banco de dados ou contrato entre frontend e backend — puramente apresentacional.

## Capabilities

### New Capabilities
Nenhuma — refinamento de capacidades já existentes.

### Modified Capabilities
- `scenario-screen`: período do cenário exibido em dd/mm/aaaa na listagem
- `opportunity-map-screen`: datas de início, intervalos e título do detalhe da oportunidade em dd/mm/aaaa
- `metrics-dashboard`: data/hora de execução e primeira data livre em dd/mm/aaaa (hh:mm quando aplicável)
- `comparison-screen`: período comparado e data de execução no histórico em dd/mm/aaaa
- `instructor-schedule-screen`: intervalo de datas da agenda e primeira data livre em dd/mm/aaaa
- `current-state-screen`: datas de início e término previsto das turmas em andamento em dd/mm/aaaa
- `non-teaching-dates-screen`: intervalo de datas não letivas em dd/mm/aaaa

## Impact

- **Frontend**: novo utilitário `frontend/src/utils/data.ts`; edições em `pages/simulacao/resultado/MapaOportunidades.tsx`, `pages/simulacao/resultado/PainelIndicadores.tsx`, `pages/simulacao/resultado/LinhaDoTempoOportunidades.tsx`, `pages/simulacao/AgendaPage.tsx`, `pages/simulacao/CenariosPage.tsx`, `pages/simulacao/ComparacaoPage.tsx`, `pages/simulacao/HistoricoPage.tsx`, `pages/simulacao/SeletorSimulacao.tsx`, `pages/dados/SituacaoAtualPage.tsx`, `pages/dados/DatasNaoLetivasPage.tsx`.
- **Backend**: nenhum.
- **Testes**: nenhum teste automatizado de frontend hoje cobre formatação de data (projeto não tem suíte de testes de frontend); verificação é manual.

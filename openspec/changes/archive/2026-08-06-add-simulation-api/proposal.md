## Why

O motor CP-SAT resolve o problema, mas roda apenas por script. A equipe de mobilização precisa acessá-lo pelo navegador, salvar diferentes configurações de prioridade e **comparar cenários** — é comparando que se descobre qual arranjo aproveita melhor a equipe.

Além disso, uma simulação pode levar minutos no teto de escala. Executá-la de forma síncrona travaria a interface sem nenhum sinal de progresso.

## What Changes

- **Cenários de simulação**: CRUD com período, escopo de projetos, flag de compartilhamento entre projetos e pesos do objetivo, persistidos em JSON
- **Execução assíncrona**: a simulação é disparada e acompanhada por consulta de status, sem bloquear o cliente
- **Persistência do resultado**: turmas sugeridas, calendários de encontros, KPIs e snapshot da capacidade usada, tudo em SQLite
- **Mapa de oportunidades**: consulta que responde, por tipologia, a partir de quando é possível abrir turma e com quais instrutores
- **Comparação de cenários**: KPIs de várias simulações lado a lado
- **Exportação** do resultado em planilha
- **Histórico** de simulações executadas

## Capabilities

### New Capabilities
- `simulation-scenarios`: definição e persistência dos cenários e seus parâmetros em JSON
- `simulation-execution`: disparo assíncrono, acompanhamento de status e persistência do resultado
- `opportunity-map`: consulta das oportunidades de abertura por tipologia e data
- `scenario-comparison`: comparação de KPIs entre simulações
- `result-export`: exportação do resultado em planilha

### Modified Capabilities
Nenhuma — todas as capacidades são novas.

## Impact

- **Novo**: `backend/app/api/{cenarios,simulacoes}.py`
- **Novo**: `backend/app/services/cenarios/` para leitura e escrita dos JSONs de parâmetros
- **Novo**: `backend/app/services/exportacao/` para geração das planilhas de resultado
- **Consome**: o motor de `add-class-opening-simulator` e os dados de `add-data-ingestion`
- **Bloqueia**: as telas de simulação do frontend dependem destes endpoints

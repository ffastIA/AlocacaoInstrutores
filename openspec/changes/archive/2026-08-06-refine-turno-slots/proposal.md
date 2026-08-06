## Why

O modelo atual trata cada turno (manhã/tarde/noite) como um "balde de horas" declarado por instrutor, permitindo múltiplas turmas no mesmo turno desde que a soma das horas caiba na capacidade. Isso não reflete a operação real: manhã e tarde têm dois horários fixos e encadeados cada (ex.: 7h–9h e 9h30–11h30), enquanto a noite tem só um. O modelo precisa expressar 5 slots reais, cada um comportando no máximo uma turma por vez.

## What Changes

- **BREAKING**: `Turno` passa de 3 valores (`manha`, `tarde`, `noite`) para 5 (`manha_1`, `manha_2`, `tarde_1`, `tarde_2`, `noite`)
- **BREAKING**: capacidade por turno deixa de ser em horas declaradas — cada slot comporta no máximo 1 turma por vez (ocupação binária). O campo `carga_horaria_horas` por turno é removido do modelo, dos parsers, da API e das telas
- Planilha de instrutores: coluna `turnos` passa a usar os 5 valores de slot; coluna `carga_horaria_turno` é removida
- Planilha de turmas em andamento: coluna `turno` passa a usar os 5 valores de slot; o alerta de sobrecarga passa de "soma de horas acima do declarado" para "sobreposição de datas no mesmo slot" (continua como alerta, nunca rejeição)
- Solver: a restrição de capacidade horária por turno é substituída por uma restrição de no-máximo-uma-turma por `(instrutor, slot, data)`; a regra de teto de 4 turmas/dia é **removida** (o teto físico de 5 slots já é a capacidade precisa)
- "Primeira data livre" por instrutor passa a ser o mínimo entre as primeiras datas livres de cada slot (não mais o máximo entre os 3 turnos), com detalhamento por slot disponível na API
- Métricas de utilização e capacidade migram de horas para contagem de slots (`slots_disponiveis`, `slots_ocupados`); `horas_formacao_total` continua em horas (mede formação entregue, não ocupação de agenda)
- Telas afetadas: Cadastros/Instrutores (editor de turnos sem carga horária), Situação Atual (seletor de turno com 5 opções, sem checagem client-side de sobrecarga), Agenda por Instrutor e Painel de Indicadores (capacidade em slots, não horas)
- Scripts VBS de planilha de teste (`ScriptVB/`) atualizados para o novo formato

## Capabilities

### New Capabilities
Nenhuma — refinamento de capacidades já existentes.

### Modified Capabilities
- `data-model`: `Turno` com 5 valores; `InstrutorTurno` sem `carga_horaria_horas`
- `instructor-import`: planilha de instrutores sem coluna de carga horária, turno com 5 valores
- `ongoing-classes`: planilha de turmas em andamento com turno de 5 valores; alerta de sobrecarga por sobreposição de datas em vez de soma de horas
- `allocation-solver`: restrição de capacidade por slot (não mais por horas); remoção do teto de 4 turmas/dia
- `candidate-generation`: remoção da poda por "horas por encontro acima da capacidade do turno"
- `simulation-metrics`: primeira data livre como mínimo entre slots, com detalhamento por slot; utilização e capacidade de reposição em contagem de slots
- `registry-screens`: edição de instrutor sem campo de carga horária por turno
- `current-state-screen`: turno de turma em andamento com 5 opções; remoção do alerta client-side de sobrecarga por horas
- `instructor-schedule-screen`: visão consolidada com slots em vez de horas
- `metrics-dashboard`: capacidade de reposição às sextas em contagem de slots

## Impact

- **Banco de dados**: nova migração Alembic remapeando valores antigos de turno e removendo a coluna `carga_horaria_horas`
- **Backend**: modelos, parsers de importação, gerador de candidatas, restrições CP-SAT, cálculo de métricas, schemas e endpoints da API
- **Frontend**: telas de Cadastros, Situação Atual, Agenda por Instrutor e Painel de Indicadores
- **Scripts de apoio**: `ScriptVB/gerar_planilhas_teste.vbs` e `ScriptVB/gerar_planilha_turmas_andamento.vbs`
- **Testes**: parte substancial da suíte de backend que constrói dados de turno precisa de atualização

## Context

O modelo de `Turno` foi implementado com 3 valores e capacidade em horas por turno (um "balde de horas" onde múltiplas turmas cabem se a soma das horas por encontro não ultrapassar o declarado). O negócio esclareceu que a operação real tem 5 horários fixos e encadeados: dois pela manhã, dois à tarde, um à noite — cada um comportando no máximo uma turma por vez. Duas decisões já foram fechadas com o usuário nesta conversa e não devem ser reabertas: (1) capacidade binária por slot, sem conceito de horas declaradas; (2) primeira data livre por slot é sempre `data_fim + 1 dia`, sem arredondamento de semana.

## Goals / Non-Goals

**Goals:**
- Expressar os 5 slots reais como o novo vocabulário de `Turno`
- Tornar a checagem de capacidade uma restrição binária simples (ocupado/livre), eliminando a necessidade de `carga_horaria_horas`
- Manter a filosofia de "aceitar e alertar, nunca rejeitar silenciosamente" para sobreposições na importação de turmas em andamento
- Preservar a precisão de "primeira data livre" por slot em vez de uma agregação grosseira

**Non-Goals:**
- Não introduzir horários de relógio explícitos (o sistema continua tratando slots como unidades abstratas de turno, sem gravar "7h–9h" literalmente)
- Não reintroduzir uma restrição de fadiga (teto de turmas/dia) nesta mudança — fica como extensão futura de uma linha, se necessário

## Decisions

### Capacidade binária por slot, sem horas declaradas
Cada um dos 5 slots comporta no máximo 1 turma por vez — decisão fechada com o usuário. O campo `carga_horaria_horas` em `InstrutorTurno` é removido; a compatibilidade entre tipologia e turno deixa de existir como conceito (qualquer tipologia cabe em qualquer slot disponível). *Alternativa considerada e descartada:* manter horas por slot, permitindo, em teoria, mais de uma turma por slot — rejeitada explicitamente pelo usuário.

### Teto de 4 turmas/dia removido
Com 5 slots binários independentes, o teto físico diário já é precisamente 5 (um por slot). Manter "4" como valor arbitrário herdado do modelo antigo contradiria a precisão que o modelo de slots introduz. Se o negócio quiser reintroduzir um teto de fadiga menor no futuro, é uma restrição de uma linha (`AddLinearConstraint`) a adicionar depois, com uma justificativa de negócio nova, não herdada.

### Primeira data livre: mínimo entre slots, com detalhamento por slot
"Primeira data livre" por instrutor passa a ser o `min()` entre a data de liberação de cada slot (antes era `max()` entre os 3 turnos). Com um modelo de 3 turnos, `max()` já era uma aproximação grosseira; com 5 slots independentes, escondia oportunidades reais de curto prazo (um instrutor livre amanhã em `manha_1` mas ocupado por meses à noite reportaria "livre em meses"). O endpoint de capacidade por instrutor passa a expor tanto o valor agregado (`min()`, para ordenação e visão geral) quanto o detalhamento por slot.

### Sobrecarga na importação de turmas em andamento: sobreposição de datas, não soma de horas
Sem conceito de horas por slot, a única violação possível de "no máximo 1 turma por slot" é duas turmas do mesmo instrutor no mesmo slot com intervalos de datas sobrepostos. Continua como alerta na importação (nunca rejeição) — mantém a filosofia já documentada no parser de que isso é "o retrato do mundo real, não um erro de preenchimento". A checagem client-side equivalente em `SituacaoAtualPage.tsx` é removida em vez de reimplementada: o formulário manual de cadastro nunca teve checagem equivalente, e duplicar a detecção de sobreposição no cliente sem necessidade contradiz a simplicidade do restante do app.

### Métricas de capacidade em contagem de slots, não horas
`slots_disponiveis`/`slots_ocupados`/`utilizacao_percentual` substituem `horas_disponiveis`/`horas_alocadas`. `horas_formacao_total` continua em horas — é uma métrica diferente (quanto de formação foi entregue), não de ocupação de agenda, e não deve ser confundida com a métrica de capacidade.

### Migração do banco: mapeamento best-effort, não bloqueante
A migração remapeia `manha→manha_1` e `tarde→tarde_1` como padrão razoável, sabendo que é impossível reconstruir, a partir dos dados antigos, qual dos dois slots era realmente usado (o modelo antigo nunca distinguiu). Prosseguir com a migração e pedir revisão manual da equipe depois é preferível a bloquear a mudança por causa de um único banco de desenvolvimento com poucos registros.

## Risks / Trade-offs

- **Mapeamento manha→manha_1/tarde→tarde_1 é arbitrário** → mitigado por ser dado de desenvolvimento (poucos registros), com necessidade de revisão manual pós-migração documentada
- **Remoção do teto de 4 turmas/dia pode surpreender quem espera o comportamento antigo** → mitigado por ser precisamente substituído pelo teto natural de 5 slots, mais preciso, não uma remoção de controle
- **Grande superfície de testes afetada (~90-120 de 272)** → mitigado por atualizar teste a teste junto com cada arquivo de produção correspondente, não como etapa separada ao final

## Migration Plan

Nova revisão Alembic: `UPDATE` de valores de turno em `instrutor_turno`, `turmas_em_andamento`, `turmas_sugeridas`, `turma_sugerida_encontro` (`manha→manha_1`, `tarde→tarde_1`, `noite` inalterado), seguido de `batch_alter_table` removendo `carga_horaria_horas` e seu `CheckConstraint` de `instrutor_turno`. `downgrade()` reverte de forma best-effort (documentado como lossy, já que dois slots colapsam em um turno).

## Open Questions

Nenhuma pendente — as duas decisões de negócio necessárias já foram fechadas com o usuário nesta conversa (capacidade binária por slot; sem arredondamento de semana). A remoção do teto de 4 turmas/dia é uma recomendação técnica deste design, não uma pergunta em aberto.

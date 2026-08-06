## MODIFIED Requirements

### Requirement: Respeito à capacidade horária por turno
O sistema SHALL garantir que cada slot de turno (`manha_1`, `manha_2`, `tarde_1`, `tarde_2`, `noite`) de um instrutor tenha no máximo uma turma ativa por vez.

#### Scenario: Slot livre em um dia
- **WHEN** um instrutor tem um slot sem nenhuma turma naquele dia
- **THEN** o solver pode alocar uma turma candidata naquele slot e dia

#### Scenario: Slot já ocupado
- **WHEN** um slot de um instrutor já tem uma turma (em andamento ou já selecionada pelo solver) naquele dia
- **THEN** o solver não aloca nenhuma outra turma candidata naquele mesmo slot e dia

#### Scenario: Capacidade consumida por turma em andamento
- **WHEN** uma turma em andamento já ocupa um slot de um instrutor
- **THEN** o solver não aloca nenhuma turma sugerida naquele slot enquanto a turma em andamento não terminar

### Requirement: Aproveitamento de capacidade residual
O sistema SHALL permitir que um instrutor assuma nova turma sem ter encerrado as atuais, desde que haja um slot livre em algum dia da modalidade.

#### Scenario: Slot livre durante turma em andamento
- **WHEN** um instrutor tem turma em andamento em `manha_1` e o slot `tarde_1` está livre
- **THEN** o solver pode alocar uma turma sugerida em `tarde_1` antes do término da turma em `manha_1`

### Requirement: Encadeamento de turmas ao longo do período
O sistema SHALL simular a sequência completa de aberturas no período, permitindo que um instrutor receba turmas sucessivas no mesmo slot conforme sua capacidade se libera.

#### Scenario: Turmas sucessivas
- **WHEN** o período simulado comporta três turmas consecutivas de uma tipologia no mesmo slot de um instrutor
- **THEN** o solver pode alocar as três, cada uma iniciando após o término da anterior

#### Scenario: Sem sobreposição indevida
- **WHEN** duas turmas sugeridas são alocadas ao mesmo instrutor no mesmo slot
- **THEN** seus calendários de encontros não se sobrepõem em nenhuma data

## REMOVED Requirements

### Requirement: Teto de turmas por dia
**Reason**: com 5 slots binários independentes por instrutor, o teto físico diário já é precisamente 5 (um por slot) — mantê-lo em 4 seria um valor arbitrário herdado do modelo antigo, sem justificativa de negócio própria no modelo de slots.
**Migration**: nenhuma ação necessária; o limite de turmas por dia passa a ser o número de slots do instrutor. Se o negócio quiser reintroduzir um teto de fadiga menor, é uma nova restrição a definir com justificativa própria.

## MODIFIED Requirements

### Requirement: Agenda de ocupação por instrutor
O sistema SHALL apresentar, para cada instrutor, sua ocupação ao longo do período simulado.

#### Scenario: Visão da agenda
- **WHEN** o usuário consulta a agenda de um instrutor
- **THEN** a interface exibe suas turmas em andamento e sugeridas, com tipologia, turno e intervalo de datas

#### Scenario: Distinção entre confirmado e sugerido
- **WHEN** a agenda exibe turmas de ambas as origens
- **THEN** cada turma indica visualmente se é alocação em andamento ou sugestão da simulação

#### Scenario: Capacidade livre
- **WHEN** a agenda é exibida
- **THEN** a interface indica os turnos e períodos em que o instrutor ainda tem capacidade disponível

#### Scenario: Instrutor sem alocação
- **WHEN** um instrutor não recebe nenhuma turma na simulação
- **THEN** a interface o exibe como integralmente disponível no período

#### Scenario: Formato do intervalo de datas
- **WHEN** a agenda exibe o intervalo de datas de uma turma
- **THEN** as datas de início e término aparecem no formato dd/mm/aaaa

### Requirement: Visão consolidada da equipe
O sistema SHALL permitir comparar a ocupação entre instrutores.

#### Scenario: Listagem por utilização
- **WHEN** o usuário acessa a visão consolidada
- **THEN** a interface lista os instrutores com seus slots ocupados, slots disponíveis e utilização percentual

#### Scenario: Identificação de ociosidade
- **WHEN** a listagem é exibida
- **THEN** a interface permite ordenar por utilização, evidenciando quem está mais ocioso

#### Scenario: Filtro por projeto
- **WHEN** o usuário filtra por projeto
- **THEN** a listagem exibe apenas os instrutores daquele projeto

### Requirement: Primeira data livre
O sistema SHALL destacar, para cada instrutor, a partir de quando ele tem capacidade disponível.

#### Scenario: Instrutor ocupado
- **WHEN** um instrutor tem capacidade integralmente ocupada até determinada data
- **THEN** a interface destaca essa data como sua primeira disponibilidade

#### Scenario: Ordenação por liberação
- **WHEN** a listagem é exibida
- **THEN** a interface permite ordenar pela primeira data livre, evidenciando quem libera capacidade antes

#### Scenario: Formato da data exibida
- **WHEN** a interface destaca a primeira data livre de um instrutor
- **THEN** a data aparece no formato dd/mm/aaaa

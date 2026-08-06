## MODIFIED Requirements

### Requirement: Primeira data livre por instrutor
O sistema SHALL informar, para cada instrutor, a primeira data em que ele passa a ter algum slot de turno disponível, calculada como o mínimo entre as primeiras datas livres de cada um dos seus slots.

#### Scenario: Instrutor com slot ocupado
- **WHEN** um slot de um instrutor está ocupado até determinada data
- **THEN** o sistema reporta o dia seguinte como a primeira data livre daquele slot

#### Scenario: Instrutor com múltiplos slots
- **WHEN** um instrutor tem um slot livre em breve e outro ocupado por meses
- **THEN** o sistema reporta como sua primeira data livre a menor das datas de liberação entre os slots, e disponibiliza o detalhamento por slot

#### Scenario: Instrutor sem alocação
- **WHEN** um instrutor não tem nenhuma turma em andamento
- **THEN** o sistema reporta o início do período simulado como sua primeira data livre em todos os slots

### Requirement: Distribuição por tipologia e por instrutor
O sistema SHALL reportar quantas turmas foram sugeridas por tipologia e qual a utilização percentual de cada instrutor, com os respectivos índices de equilíbrio.

#### Scenario: Distribuição por tipologia
- **WHEN** a simulação sugere turmas de três tipologias diferentes
- **THEN** o sistema reporta a contagem de turmas de cada uma e um índice de equilíbrio entre elas

#### Scenario: Utilização por instrutor
- **WHEN** a simulação é concluída
- **THEN** o sistema reporta, para cada instrutor, os slots disponíveis, os slots ocupados e a utilização percentual entre eles

### Requirement: Capacidade de reposição às sextas
O sistema SHALL reportar a capacidade de slots disponíveis às sextas-feiras, derivada dos instrutores que declararam disponibilidade no dia 6.

#### Scenario: Instrutores com disponibilidade às sextas
- **WHEN** parte dos instrutores declara disponibilidade no dia 6
- **THEN** o sistema reporta a quantidade de slots de reposição disponíveis, sem alocar nenhuma turma regular nesse dia

# simulation-metrics Specification

## Purpose
TBD - created by archiving change add-class-opening-simulator. Update Purpose after archive.
## Requirements
### Requirement: Indicador de ociosidade
O sistema SHALL calcular o percentual de ociosidade como a fração da capacidade disponível que não foi aproveitada pelas turmas sugeridas e em andamento.

#### Scenario: Capacidade totalmente aproveitada
- **WHEN** todas as horas disponíveis dos instrutores são ocupadas
- **THEN** o sistema reporta ociosidade de zero por cento

#### Scenario: Capacidade parcialmente aproveitada
- **WHEN** metade das horas disponíveis é ocupada
- **THEN** o sistema reporta ociosidade de cinquenta por cento

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

### Requirement: Leque de tipologias possíveis por data
O sistema SHALL informar, ao longo do período, quais tipologias podem ser abertas a partir de cada data e quais instrutores as sustentam.

#### Scenario: Instrutor multi-tipologia liberando capacidade
- **WHEN** um instrutor que domina duas tipologias libera capacidade em determinada data
- **THEN** o sistema reporta ambas as tipologias como possíveis a partir daquela data, indicando esse instrutor como quem as sustenta

#### Scenario: Tipologia sem instrutor disponível
- **WHEN** nenhum instrutor apto a uma tipologia tem capacidade livre em determinada data
- **THEN** essa tipologia não aparece entre as possíveis naquela data

### Requirement: Capacidade de reposição às sextas
O sistema SHALL reportar a capacidade de slots disponíveis às sextas-feiras, derivada dos instrutores que declararam disponibilidade no dia 6.

#### Scenario: Instrutores com disponibilidade às sextas
- **WHEN** parte dos instrutores declara disponibilidade no dia 6
- **THEN** o sistema reporta a quantidade de slots de reposição disponíveis, sem alocar nenhuma turma regular nesse dia

### Requirement: Metadados de execução
O sistema SHALL reportar o total de turmas sugeridas, as horas de formação resultantes, o valor do objetivo, o status do solver e o tempo de execução.

#### Scenario: Resumo da execução
- **WHEN** uma simulação é concluída
- **THEN** o sistema reporta esses metadados junto ao resultado, permitindo avaliar a qualidade e o custo da busca


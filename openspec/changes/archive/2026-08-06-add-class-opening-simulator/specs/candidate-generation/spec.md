## ADDED Requirements

### Requirement: Enumeração de turmas candidatas
O sistema SHALL enumerar as turmas candidatas como combinações de instrutor, tipologia, turno, modalidade e semana de início dentro do período simulado.

#### Scenario: Instrutor multi-tipologia
- **WHEN** um instrutor domina Programação e Pixel Art, está disponível em um turno e a modalidade é única
- **THEN** o sistema gera candidatas para ambas as tipologias em cada semana de início viável

#### Scenario: Turma que não cabe no período
- **WHEN** uma semana de início faria a turma terminar após o fim do período simulado
- **THEN** o sistema não gera candidata para aquela semana

### Requirement: Poda por elegibilidade
O sistema SHALL descartar na enumeração — sem criar variável de decisão — toda combinação inviável.

#### Scenario: Tipologia não dominada
- **WHEN** uma tipologia não consta nas habilidades do instrutor
- **THEN** nenhuma candidata é gerada para aquele par instrutor–tipologia

#### Scenario: Turno indisponível
- **WHEN** um turno não consta na disponibilidade do instrutor
- **THEN** nenhuma candidata é gerada para aquele par instrutor–turno

#### Scenario: Dias da semana incompatíveis com a modalidade
- **WHEN** um instrutor está disponível apenas às segundas e quartas
- **THEN** o sistema gera candidatas na modalidade `regular_seg_qua`, mas nenhuma nas modalidades `regular_ter_qui` e `intensiva_seg_qui`

#### Scenario: Horas por encontro acima da capacidade do turno
- **WHEN** uma tipologia exige 4 horas por encontro e o instrutor tem apenas 3 horas de capacidade naquele turno
- **THEN** nenhuma candidata é gerada para aquela combinação

#### Scenario: Semana anterior à liberação do instrutor
- **WHEN** o instrutor não tem nenhuma capacidade livre antes de determinada data
- **THEN** nenhuma candidata é gerada com semana de início anterior a essa data

### Requirement: Escopo de projetos
O sistema SHALL restringir as candidatas ao escopo de projetos da simulação, com compartilhamento de instrutores entre projetos configurável.

#### Scenario: Compartilhamento desligado
- **WHEN** a simulação abrange dois projetos com o compartilhamento desligado
- **THEN** cada turma candidata pertence ao mesmo projeto do seu instrutor

#### Scenario: Compartilhamento ligado
- **WHEN** a simulação abrange dois projetos com o compartilhamento ligado
- **THEN** os instrutores formam um pool único, e a origem de projeto deixa de restringir as candidatas

#### Scenario: Projeto fora do escopo
- **WHEN** um instrutor pertence a um projeto que não está no escopo da simulação
- **THEN** nenhuma candidata é gerada para esse instrutor

### Requirement: Catálogo de tipologias limitado às habilidades existentes
O sistema SHALL restringir as tipologias ofertáveis à união das habilidades dos instrutores no escopo.

#### Scenario: Tipologia sem instrutor apto
- **WHEN** existe no catálogo uma tipologia que nenhum instrutor do escopo domina
- **THEN** nenhuma candidata é gerada para essa tipologia

## MODIFIED Requirements

### Requirement: Modelo de projetos e instrutores
O sistema SHALL modelar instrutores vinculados a um projeto, cada um com seus slots de turno disponíveis (`manha_1`, `manha_2`, `tarde_1`, `tarde_2`, `noite`), dias da semana disponíveis e tipologias que domina.

#### Scenario: Instrutor com múltiplos slots
- **WHEN** um instrutor é gravado com disponibilidade em `manha_1`, `manha_2` e `noite`
- **THEN** o sistema persiste três registros de slot associados ao mesmo instrutor, sem carga horária declarada por slot

#### Scenario: Instrutor com múltiplas tipologias
- **WHEN** um instrutor domina Programação e Pixel Art
- **THEN** o sistema persiste dois vínculos na relação N:N entre instrutor e tipologia

#### Scenario: Dias da semana disponíveis
- **WHEN** um instrutor está disponível às segundas e quartas
- **THEN** o sistema persiste os dias `2` e `4` como registros de disponibilidade daquele instrutor

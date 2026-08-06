# metrics-dashboard Specification

## Purpose
TBD - created by archiving change add-frontend-simulation-screens. Update Purpose after archive.
## Requirements
### Requirement: Painel de indicadores da simulação
O sistema SHALL apresentar os indicadores de resultado de uma simulação concluída.

#### Scenario: Indicadores principais
- **WHEN** o usuário acessa o painel de uma simulação concluída
- **THEN** a interface exibe o percentual de ociosidade, o total de turmas sugeridas, as horas de formação resultantes e os índices de equilíbrio de carga e de tipologias

#### Scenario: Distribuição por tipologia
- **WHEN** o painel é exibido
- **THEN** a interface apresenta quantas turmas foram sugeridas por tipologia

#### Scenario: Utilização por instrutor
- **WHEN** o painel é exibido
- **THEN** a interface apresenta a distribuição de utilização entre os instrutores

#### Scenario: Formato da primeira data livre
- **WHEN** o painel exibe a primeira data livre de um instrutor
- **THEN** a data aparece no formato dd/mm/aaaa

### Requirement: Interpretação dos indicadores
O sistema SHALL explicar o significado de cada indicador para leitores sem familiaridade com otimização.

#### Scenario: Consulta ao significado
- **WHEN** o usuário consulta a explicação de um indicador
- **THEN** a interface descreve, em linguagem direta, o que ele mede e como interpretá-lo

#### Scenario: Composição do resultado
- **WHEN** o painel é exibido
- **THEN** a interface informa os pesos do objetivo que produziram aquele resultado, tornando explícita a relação entre prioridades escolhidas e resultado obtido

### Requirement: Capacidade de reposição
O sistema SHALL apresentar a capacidade disponível às sextas-feiras.

#### Scenario: Exibição da reposição
- **WHEN** o painel é exibido
- **THEN** a interface informa as horas de reposição disponíveis às sextas, esclarecendo que esse dia não recebe turma regular

### Requirement: Metadados da execução
O sistema SHALL apresentar as informações de execução da simulação.

#### Scenario: Dados da execução
- **WHEN** o painel é exibido
- **THEN** a interface informa a data e hora da execução, o tempo consumido e a qualidade da solução encontrada

#### Scenario: Formato de data e hora da execução
- **WHEN** o painel exibe a data e hora de execução
- **THEN** elas aparecem no formato dd/mm/aaaa hh:mm


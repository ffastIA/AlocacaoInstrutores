## MODIFIED Requirements

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

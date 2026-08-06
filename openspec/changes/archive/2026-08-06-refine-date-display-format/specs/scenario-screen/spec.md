## MODIFIED Requirements

### Requirement: Listagem de cenários
O sistema SHALL apresentar os cenários cadastrados com seus parâmetros.

#### Scenario: Visão da listagem
- **WHEN** o usuário acessa a tela de cenários
- **THEN** a interface exibe nome, período, escopo de projetos e pesos de cada cenário, com a ação de executar

#### Scenario: Nenhum cenário cadastrado
- **WHEN** não existe cenário algum
- **THEN** a interface exibe estado vazio orientando a criar o primeiro

#### Scenario: Formato do período exibido
- **WHEN** a listagem exibe o período de um cenário
- **THEN** as datas de início e fim aparecem no formato dd/mm/aaaa

## ADDED Requirements

### Requirement: Configuração de cenário
O sistema SHALL permitir criar e editar cenários informando período simulado, escopo de projetos, compartilhamento entre projetos e pesos do objetivo.

#### Scenario: Criação de cenário
- **WHEN** o usuário informa nome, período, escopo e pesos, e confirma
- **THEN** a interface persiste o cenário e o disponibiliza para execução

#### Scenario: Seleção do período
- **WHEN** o usuário define o período simulado
- **THEN** a interface aceita data inicial e final e impede confirmação com data final anterior à inicial

#### Scenario: Escopo de projetos
- **WHEN** o usuário seleciona os projetos a simular
- **THEN** a interface permite escolher um ou vários, e indica que deixar vazio abrange todos

#### Scenario: Compartilhamento entre projetos
- **WHEN** o usuário alterna o compartilhamento de instrutores entre projetos
- **THEN** a interface explica o efeito da opção sobre quais instrutores podem atender quais turmas

### Requirement: Ajuste dos pesos do objetivo
O sistema SHALL permitir ajustar os quatro pesos que orientam a otimização, comunicando o efeito de cada um.

#### Scenario: Ajuste dos pesos
- **WHEN** o usuário ajusta os pesos de aproveitamento, antecipação, equilíbrio de carga e equilíbrio de tipologias
- **THEN** a interface reflete os valores escolhidos e descreve, em linguagem direta, o que cada critério privilegia

#### Scenario: Todos os pesos zerados
- **WHEN** o usuário zera todos os pesos
- **THEN** a interface impede a confirmação, explicando que é preciso ao menos um critério de otimização

#### Scenario: Peso negativo
- **WHEN** o usuário informa um peso negativo
- **THEN** a interface impede a confirmação informando que os pesos devem ser não negativos

### Requirement: Duplicação de cenário
O sistema SHALL permitir duplicar um cenário existente para variar apenas o que se deseja comparar.

#### Scenario: Duplicação
- **WHEN** o usuário duplica um cenário
- **THEN** a interface cria uma cópia com os mesmos parâmetros, pronta para ajuste e nova execução

### Requirement: Listagem de cenários
O sistema SHALL apresentar os cenários cadastrados com seus parâmetros.

#### Scenario: Visão da listagem
- **WHEN** o usuário acessa a tela de cenários
- **THEN** a interface exibe nome, período, escopo de projetos e pesos de cada cenário, com a ação de executar

#### Scenario: Nenhum cenário cadastrado
- **WHEN** não existe cenário algum
- **THEN** a interface exibe estado vazio orientando a criar o primeiro

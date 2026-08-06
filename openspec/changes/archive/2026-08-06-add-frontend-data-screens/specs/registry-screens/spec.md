## ADDED Requirements

### Requirement: Listagem de instrutores
O sistema SHALL apresentar os instrutores cadastrados com sua disponibilidade e habilidades.

#### Scenario: Visão da listagem
- **WHEN** o usuário acessa a tela de instrutores
- **THEN** a interface exibe nome, projeto, turnos com respectiva carga horária, dias da semana e tipologias de cada instrutor

#### Scenario: Filtro por projeto e tipologia
- **WHEN** o usuário filtra por projeto ou por tipologia
- **THEN** a listagem exibe apenas os instrutores correspondentes

#### Scenario: Base vazia
- **WHEN** nenhum instrutor foi importado ainda
- **THEN** a interface exibe estado vazio orientando a importar a planilha de instrutores

### Requirement: Edição de instrutor
O sistema SHALL permitir ajustar a disponibilidade e as habilidades de um instrutor sem exigir reimportação da planilha.

#### Scenario: Alteração de disponibilidade
- **WHEN** o usuário altera os turnos, cargas horárias ou dias de um instrutor e confirma
- **THEN** a interface persiste a alteração e reflete o novo estado na listagem

#### Scenario: Erro de validação
- **WHEN** a alteração é rejeitada pelo backend
- **THEN** a interface exibe o motivo junto ao campo correspondente, preservando os dados já preenchidos

### Requirement: Configuração de tipologias
O sistema SHALL permitir configurar a carga horária total e as horas por encontro de cada tipologia.

#### Scenario: Configuração de tipologia pendente
- **WHEN** o usuário informa carga horária total e horas por encontro de uma tipologia pendente
- **THEN** a interface persiste a configuração e remove a marcação de pendente

#### Scenario: Carga horária incompatível
- **WHEN** o usuário informa carga horária total que não é múltiplo exato das horas por encontro
- **THEN** a interface exibe o erro explicando que o número de encontros não fecha em valor inteiro

#### Scenario: Número de encontros previsto
- **WHEN** o usuário preenche carga horária total e horas por encontro
- **THEN** a interface exibe o número de encontros resultante antes da confirmação

### Requirement: Destaque das tipologias pendentes
O sistema SHALL evidenciar as tipologias que ainda bloqueiam a execução de simulações.

#### Scenario: Existência de pendências
- **WHEN** há tipologias sem carga horária configurada
- **THEN** a interface as destaca e informa que a simulação permanece bloqueada até que sejam configuradas

#### Scenario: Tipologia sem instrutor
- **WHEN** uma tipologia não é dominada por nenhum instrutor
- **THEN** a interface a sinaliza como nunca ofertável, sem tratá-la como pendência bloqueante

### Requirement: Gestão de projetos
O sistema SHALL permitir consultar e cadastrar projetos.

#### Scenario: Listagem de projetos
- **WHEN** o usuário acessa a tela de projetos
- **THEN** a interface exibe os projetos com a quantidade de instrutores vinculados a cada um

#### Scenario: Cadastro manual
- **WHEN** o usuário cadastra um projeto não presente nas planilhas
- **THEN** a interface persiste o registro e o disponibiliza para vínculo de instrutores

## ADDED Requirements

### Requirement: Definição de cenário de simulação
O sistema SHALL permitir criar, consultar, editar e remover cenários contendo período simulado, escopo de projetos, flag de compartilhamento entre projetos e pesos do objetivo.

#### Scenario: Criação de cenário
- **WHEN** o usuário cria um cenário com período, escopo e pesos
- **THEN** o sistema persiste os metadados em SQLite e os parâmetros em arquivo JSON, retornando o identificador do cenário

#### Scenario: Edição dos pesos
- **WHEN** o usuário altera os pesos de um cenário existente
- **THEN** o sistema atualiza o arquivo JSON sem afetar as simulações já executadas a partir daquele cenário

#### Scenario: Duplicação de cenário
- **WHEN** o usuário duplica um cenário existente
- **THEN** o sistema cria um novo cenário com os mesmos parâmetros e um novo arquivo JSON, permitindo variar apenas o que interessa comparar

### Requirement: Persistência dos parâmetros em JSON
O sistema SHALL gravar os parâmetros de cada cenário em arquivo JSON versionado, contendo período, escopo, pesos, fatores de normalização, restrições e limites do solver.

#### Scenario: Estrutura do arquivo
- **WHEN** um cenário é gravado
- **THEN** o arquivo JSON contém a versão do esquema, o período, o escopo de projetos, os pesos do objetivo, os fatores de normalização e a configuração do solver

#### Scenario: Leitura de cenário existente
- **WHEN** uma simulação é executada a partir de um cenário
- **THEN** o sistema lê os parâmetros do arquivo JSON referenciado pelo cenário

#### Scenario: Arquivo JSON ausente ou corrompido
- **WHEN** o arquivo de parâmetros de um cenário não pode ser lido
- **THEN** o sistema retorna erro identificando o cenário e o arquivo esperado, sem tentar executar com valores padrão

### Requirement: Validação dos parâmetros do cenário
O sistema SHALL validar os parâmetros antes de aceitar o cenário.

#### Scenario: Período invertido
- **WHEN** a data final do período é anterior à inicial
- **THEN** o sistema rejeita o cenário informando a inconsistência

#### Scenario: Pesos negativos
- **WHEN** algum peso do objetivo é negativo
- **THEN** o sistema rejeita o cenário informando que os pesos devem ser não negativos

#### Scenario: Todos os pesos nulos
- **WHEN** todos os pesos do objetivo são zero
- **THEN** o sistema rejeita o cenário, pois não haveria critério de otimização

#### Scenario: Escopo de projetos vazio
- **WHEN** nenhum projeto é informado no escopo
- **THEN** o sistema assume todos os projetos cadastrados

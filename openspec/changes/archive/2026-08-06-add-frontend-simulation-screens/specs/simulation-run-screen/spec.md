## ADDED Requirements

### Requirement: Disparo da simulação
O sistema SHALL permitir executar um cenário e acompanhar o andamento até a conclusão.

#### Scenario: Início da execução
- **WHEN** o usuário executa um cenário
- **THEN** a interface confirma o início e passa a exibir o andamento sem travar a navegação

#### Scenario: Acompanhamento
- **WHEN** a simulação está em processamento
- **THEN** a interface indica que a execução está em curso e informa o tempo decorrido

#### Scenario: Conclusão
- **WHEN** a simulação conclui
- **THEN** a interface exibe o resultado automaticamente, sem exigir atualização manual da página

### Requirement: Comunicação de bloqueios
O sistema SHALL informar, de forma acionável, quando a execução não puder ocorrer.

#### Scenario: Tipologias pendentes de configuração
- **WHEN** a execução é recusada por existirem tipologias sem carga horária
- **THEN** a interface lista as tipologias pendentes e oferece acesso direto à tela de configuração

#### Scenario: Escopo sem instrutores
- **WHEN** a execução é recusada porque o escopo não contém instrutores
- **THEN** a interface informa a causa e sugere revisar o escopo do cenário ou importar instrutores

#### Scenario: Falha durante a execução
- **WHEN** a simulação termina em erro
- **THEN** a interface exibe a mensagem correspondente e mantém a opção de executar novamente

### Requirement: Comunicação do resultado da busca
O sistema SHALL informar a qualidade da solução encontrada e o custo da execução.

#### Scenario: Solução ótima
- **WHEN** o solver prova a otimalidade
- **THEN** a interface indica que a melhor solução possível foi encontrada

#### Scenario: Tempo esgotado
- **WHEN** o limite de tempo é atingido com solução viável
- **THEN** a interface indica que a busca foi interrompida por tempo e que o resultado pode não ser o ótimo

#### Scenario: Nenhuma turma viável
- **WHEN** a simulação conclui sem nenhuma turma sugerida
- **THEN** a interface explica que não há oportunidade de abertura no período, em vez de exibir uma tela vazia sem contexto

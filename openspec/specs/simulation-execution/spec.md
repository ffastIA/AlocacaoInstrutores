# simulation-execution Specification

## Purpose
TBD - created by archiving change add-simulation-api. Update Purpose after archive.
## Requirements
### Requirement: Execução assíncrona da simulação
O sistema SHALL disparar a simulação sem bloquear o cliente, retornando imediatamente um identificador para acompanhamento.

#### Scenario: Disparo da simulação
- **WHEN** o usuário solicita a execução de um cenário
- **THEN** o sistema cria o registro da simulação com status pendente, inicia o processamento em segundo plano e retorna o identificador

#### Scenario: Acompanhamento do progresso
- **WHEN** o usuário consulta uma simulação em processamento
- **THEN** o sistema retorna o status atual sem esperar a conclusão

#### Scenario: Conclusão
- **WHEN** o solver termina
- **THEN** o sistema atualiza o status para concluída e registra o tempo de execução, o status do solver e o valor do objetivo

#### Scenario: Falha durante a execução
- **WHEN** ocorre um erro durante o processamento
- **THEN** o sistema registra o status de erro com a mensagem correspondente, mantendo o registro consultável

### Requirement: Bloqueio por dados incompletos
O sistema SHALL recusar a execução quando os dados necessários não estiverem completos.

#### Scenario: Tipologia sem carga horária configurada
- **WHEN** existe no escopo uma tipologia pendente de configuração
- **THEN** o sistema recusa a execução e informa quais tipologias precisam ser configuradas

#### Scenario: Nenhum instrutor no escopo
- **WHEN** o escopo de projetos não contém nenhum instrutor
- **THEN** o sistema recusa a execução informando que não há capacidade a simular

### Requirement: Persistência do resultado
O sistema SHALL persistir as turmas sugeridas, seus calendários de encontros e os KPIs de cada simulação concluída.

#### Scenario: Turmas sugeridas gravadas
- **WHEN** uma simulação é concluída com turmas sugeridas
- **THEN** cada turma é persistida com instrutor, tipologia, projeto, modalidade, turno, datas de início e término e número de encontros

#### Scenario: Calendário de encontros gravado
- **WHEN** uma turma sugerida é persistida
- **THEN** seus encontros são gravados individualmente com data, turno e carga horária

#### Scenario: Resultado vazio
- **WHEN** a simulação conclui sem nenhuma turma viável
- **THEN** o sistema registra a simulação como concluída com zero turmas sugeridas, sem tratar isso como erro

### Requirement: Reprodutibilidade do resultado
O sistema SHALL congelar, em cada simulação, a capacidade dos instrutores utilizada na execução.

#### Scenario: Consulta posterior à mudança dos dados
- **WHEN** o usuário consulta uma simulação antiga após as turmas em andamento terem sido atualizadas
- **THEN** o sistema retorna o resultado original com a capacidade que vigorava no momento da execução

### Requirement: Consulta de resultados
O sistema SHALL disponibilizar as turmas sugeridas e os KPIs de uma simulação concluída.

#### Scenario: Consulta das turmas sugeridas
- **WHEN** o usuário consulta as turmas sugeridas de uma simulação concluída
- **THEN** o sistema retorna a lista com todos os atributos de cada turma, incluindo seu calendário

#### Scenario: Consulta dos KPIs
- **WHEN** o usuário consulta os KPIs de uma simulação concluída
- **THEN** o sistema retorna ociosidade, total de turmas, horas de formação, índices de equilíbrio e utilização por instrutor

#### Scenario: Consulta de simulação inexistente
- **WHEN** o usuário consulta um identificador que não existe
- **THEN** o sistema retorna HTTP 404

### Requirement: Histórico de simulações
O sistema SHALL manter e disponibilizar o histórico de simulações executadas.

#### Scenario: Listagem do histórico
- **WHEN** o usuário lista o histórico
- **THEN** o sistema retorna as simulações mais recentes primeiro, com cenário, status, data de execução e KPIs principais

#### Scenario: Filtro por cenário
- **WHEN** o usuário filtra o histórico por cenário
- **THEN** o sistema retorna apenas as simulações daquele cenário


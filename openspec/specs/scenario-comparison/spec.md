# scenario-comparison Specification

## Purpose
TBD - created by archiving change add-simulation-api. Update Purpose after archive.
## Requirements
### Requirement: Comparação de KPIs entre simulações
O sistema SHALL comparar os indicadores de duas ou mais simulações lado a lado.

#### Scenario: Comparação de dois cenários
- **WHEN** o usuário compara duas simulações concluídas
- **THEN** o sistema retorna, para cada uma, ociosidade, total de turmas, horas de formação e índices de equilíbrio, alinhados para leitura lado a lado

#### Scenario: Destaque das diferenças
- **WHEN** duas simulações são comparadas
- **THEN** o sistema informa a diferença de cada indicador entre elas

#### Scenario: Comparação de mais de duas simulações
- **WHEN** o usuário compara três ou mais simulações
- **THEN** o sistema retorna todas na mesma estrutura, permitindo avaliação conjunta

### Requirement: Comparabilidade dos resultados
O sistema SHALL informar os parâmetros que produziram cada resultado, para que a comparação seja interpretável.

#### Scenario: Parâmetros junto ao resultado
- **WHEN** simulações são comparadas
- **THEN** cada uma é acompanhada do seu período, escopo de projetos, flag de compartilhamento e pesos do objetivo

#### Scenario: Períodos divergentes
- **WHEN** as simulações comparadas usam períodos diferentes
- **THEN** o sistema sinaliza que os resultados não são diretamente comparáveis em valores absolutos

### Requirement: Validação da comparação
O sistema SHALL recusar comparações mal formadas.

#### Scenario: Simulação não concluída
- **WHEN** uma das simulações informadas ainda não concluiu
- **THEN** o sistema recusa a comparação informando qual delas não está pronta

#### Scenario: Identificador inexistente
- **WHEN** um dos identificadores informados não existe
- **THEN** o sistema retorna erro indicando qual identificador não foi encontrado


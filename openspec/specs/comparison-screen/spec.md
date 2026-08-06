# comparison-screen Specification

## Purpose
TBD - created by archiving change add-frontend-simulation-screens. Update Purpose after archive.
## Requirements
### Requirement: Comparação de cenários
O sistema SHALL permitir comparar os indicadores de duas ou mais simulações lado a lado.

#### Scenario: Seleção das simulações
- **WHEN** o usuário seleciona duas ou mais simulações concluídas para comparar
- **THEN** a interface exibe seus indicadores alinhados para leitura lado a lado

#### Scenario: Destaque das diferenças
- **WHEN** a comparação é exibida
- **THEN** a interface evidencia a diferença de cada indicador entre as simulações

#### Scenario: Parâmetros de cada resultado
- **WHEN** a comparação é exibida
- **THEN** cada simulação aparece acompanhada do seu período, escopo, compartilhamento e pesos do objetivo

#### Scenario: Períodos divergentes
- **WHEN** as simulações comparadas usam períodos diferentes
- **THEN** a interface alerta que os valores absolutos não são diretamente comparáveis

#### Scenario: Simulação não concluída
- **WHEN** o usuário tenta incluir na comparação uma simulação ainda em execução
- **THEN** a interface impede a seleção informando que ela ainda não está pronta

#### Scenario: Formato do período comparado
- **WHEN** a comparação exibe o período de cada simulação
- **THEN** as datas aparecem no formato dd/mm/aaaa

### Requirement: Histórico de simulações
O sistema SHALL apresentar as simulações executadas, com acesso aos respectivos resultados.

#### Scenario: Listagem do histórico
- **WHEN** o usuário acessa o histórico
- **THEN** a interface exibe as simulações mais recentes primeiro, com cenário, data de execução, status e indicadores principais

#### Scenario: Acesso ao resultado
- **WHEN** o usuário seleciona uma simulação do histórico
- **THEN** a interface abre seu mapa de oportunidades e seu painel de indicadores

#### Scenario: Filtro por cenário
- **WHEN** o usuário filtra o histórico por cenário
- **THEN** a interface exibe apenas as simulações daquele cenário, facilitando avaliar a evolução entre execuções

#### Scenario: Histórico vazio
- **WHEN** nenhuma simulação foi executada
- **THEN** a interface exibe estado vazio orientando a criar um cenário e executá-lo

#### Scenario: Formato da data de execução
- **WHEN** o histórico exibe a data de execução de uma simulação
- **THEN** ela aparece no formato dd/mm/aaaa hh:mm

### Requirement: Identificação de simulações com falha
O sistema SHALL distinguir no histórico as simulações que não concluíram com sucesso.

#### Scenario: Simulação com erro
- **WHEN** o histórico inclui uma simulação que terminou em erro
- **THEN** a interface a sinaliza como falha, exibe a mensagem correspondente e não oferece acesso a resultados inexistentes


## ADDED Requirements

### Requirement: Visualização das oportunidades de abertura
O sistema SHALL apresentar, por tipologia e ao longo do período, quais turmas podem ser abertas e a partir de qual data.

#### Scenario: Visão principal
- **WHEN** o usuário acessa o mapa de oportunidades de uma simulação concluída
- **THEN** a interface exibe, por tipologia, as datas de abertura possíveis, a quantidade de turmas em cada data e os instrutores que as sustentam

#### Scenario: Ordenação cronológica
- **WHEN** o mapa é exibido
- **THEN** as oportunidades aparecem da data mais próxima para a mais distante

#### Scenario: Instrutor multi-tipologia
- **WHEN** um instrutor que domina duas tipologias libera capacidade
- **THEN** ambas as tipologias aparecem como possíveis naquela data, deixando visível que se trata de uma escolha entre alternativas

#### Scenario: Detalhe de uma oportunidade
- **WHEN** o usuário abre o detalhe de uma turma sugerida
- **THEN** a interface exibe instrutor, modalidade, turno, datas de início e término, número de encontros e carga horária

### Requirement: Filtros do mapa
O sistema SHALL permitir restringir a visualização por tipologia, instrutor, projeto e intervalo de datas.

#### Scenario: Filtro por tipologia
- **WHEN** o usuário filtra por uma tipologia
- **THEN** o mapa exibe apenas as oportunidades daquela tipologia

#### Scenario: Filtro por intervalo
- **WHEN** o usuário restringe o intervalo de datas
- **THEN** o mapa exibe apenas as oportunidades cuja data de início está no intervalo

#### Scenario: Filtro sem resultados
- **WHEN** a combinação de filtros não retorna oportunidades
- **THEN** a interface exibe estado vazio indicando que nenhuma oportunidade corresponde aos filtros aplicados

### Requirement: Apresentação legível de dados extensos
O sistema SHALL exibir o mapa sem provocar rolagem horizontal da página inteira.

#### Scenario: Período longo com muitas tipologias
- **WHEN** o mapa excede a largura disponível
- **THEN** a rolagem horizontal ocorre dentro do próprio contêiner, mantendo visíveis a navegação e a identificação das tipologias

### Requirement: Exportação do resultado
O sistema SHALL permitir exportar o resultado da simulação em planilha a partir da tela.

#### Scenario: Exportação
- **WHEN** o usuário solicita a exportação de uma simulação concluída
- **THEN** a interface baixa o arquivo com as turmas sugeridas, os indicadores e os parâmetros do cenário

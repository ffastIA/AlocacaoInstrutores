## ADDED Requirements

### Requirement: Mapa de oportunidades por tipologia
O sistema SHALL responder, para uma simulação concluída, quais tipologias podem ser abertas a partir de cada data e com quais instrutores.

#### Scenario: Consulta do mapa
- **WHEN** o usuário consulta o mapa de oportunidades de uma simulação concluída
- **THEN** o sistema retorna, por tipologia, as datas de abertura possíveis, a quantidade de turmas em cada uma e os instrutores que as sustentam

#### Scenario: Instrutor multi-tipologia
- **WHEN** um instrutor que domina duas tipologias libera capacidade em determinada data
- **THEN** ambas as tipologias aparecem como possíveis naquela data, com esse instrutor indicado em cada uma

#### Scenario: Agrupamento por data de início
- **WHEN** várias turmas sugeridas compartilham a mesma data de início
- **THEN** o sistema as agrupa por data, facilitando o planejamento da divulgação

### Requirement: Ordenação cronológica
O sistema SHALL apresentar as oportunidades em ordem cronológica de data de início.

#### Scenario: Ordem do resultado
- **WHEN** o mapa é consultado
- **THEN** as oportunidades aparecem da data mais próxima para a mais distante

### Requirement: Agenda de ocupação por instrutor
O sistema SHALL disponibilizar, por instrutor, a ocupação ao longo do período, combinando turmas em andamento e turmas sugeridas.

#### Scenario: Consulta da agenda
- **WHEN** o usuário consulta a agenda de um instrutor
- **THEN** o sistema retorna suas turmas em andamento e sugeridas com datas e turnos, além da capacidade ainda livre em cada período

#### Scenario: Distinção entre confirmado e sugerido
- **WHEN** a agenda inclui turmas de ambas as origens
- **THEN** cada turma indica se é uma alocação em andamento ou uma sugestão da simulação

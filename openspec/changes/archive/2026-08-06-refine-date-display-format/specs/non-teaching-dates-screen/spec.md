## MODIFIED Requirements

### Requirement: Calendário de datas não letivas
O sistema SHALL apresentar os feriados, recessos e períodos de férias cadastrados.

#### Scenario: Visão da listagem
- **WHEN** o usuário acessa a tela de datas não letivas
- **THEN** a interface exibe descrição, intervalo de datas, tipo e projeto de cada registro

#### Scenario: Ordenação cronológica
- **WHEN** a listagem é exibida
- **THEN** os registros aparecem em ordem cronológica de data de início

#### Scenario: Filtro por período
- **WHEN** o usuário filtra por um intervalo
- **THEN** a interface exibe apenas os registros que interseccionam aquele intervalo

#### Scenario: Formato do intervalo exibido
- **WHEN** a listagem exibe o intervalo de datas de um registro
- **THEN** as datas aparecem no formato dd/mm/aaaa

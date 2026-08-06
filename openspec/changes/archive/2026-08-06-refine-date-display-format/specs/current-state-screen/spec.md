## MODIFIED Requirements

### Requirement: Listagem das turmas em andamento
O sistema SHALL apresentar as turmas atualmente em execução, que definem o ponto de partida das simulações.

#### Scenario: Visão da listagem
- **WHEN** o usuário acessa a tela de situação atual
- **THEN** a interface exibe instrutor, tipologia, modalidade, turno e datas de início e término prevista de cada turma

#### Scenario: Ordenação por término
- **WHEN** a listagem é exibida
- **THEN** as turmas aparecem ordenadas pela data de término prevista, evidenciando quais instrutores liberam capacidade primeiro

#### Scenario: Nenhuma turma em andamento
- **WHEN** não há turmas cadastradas
- **THEN** a interface exibe estado vazio explicando que a simulação partirá com todos os instrutores livres

#### Scenario: Formato das datas exibidas
- **WHEN** a listagem exibe a data de início ou término prevista de uma turma
- **THEN** as datas aparecem no formato dd/mm/aaaa

## ADDED Requirements

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

### Requirement: Cadastro e edição de turma em andamento
O sistema SHALL permitir registrar e ajustar turmas em andamento diretamente pela interface.

#### Scenario: Cadastro manual
- **WHEN** o usuário informa instrutor, tipologia, modalidade, turno e datas, e confirma
- **THEN** a interface persiste a turma e a exibe na listagem

#### Scenario: Turno incompatível com o instrutor
- **WHEN** o usuário seleciona um turno fora da disponibilidade do instrutor escolhido
- **THEN** a interface impede a confirmação e explica a incompatibilidade

#### Scenario: Datas inconsistentes
- **WHEN** o usuário informa data de término anterior à de início
- **THEN** a interface exibe o erro junto ao campo de data

#### Scenario: Remoção de turma
- **WHEN** o usuário remove uma turma em andamento
- **THEN** a interface confirma a intenção antes de excluir e atualiza a listagem

### Requirement: Alerta de sobrecarga
O sistema SHALL sinalizar quando as turmas em andamento ultrapassam a capacidade declarada de um instrutor.

#### Scenario: Instrutor sobrecarregado
- **WHEN** as turmas de um instrutor somam mais horas do que sua disponibilidade declarada
- **THEN** a interface sinaliza a situação como alerta, deixando claro que os dados foram aceitos

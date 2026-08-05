## ADDED Requirements

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

### Requirement: Cadastro e edição de datas não letivas
O sistema SHALL permitir registrar e ajustar datas sem aula diretamente pela interface.

#### Scenario: Cadastro de dia único
- **WHEN** o usuário informa apenas a data de início
- **THEN** a interface registra um intervalo de um único dia

#### Scenario: Cadastro de intervalo
- **WHEN** o usuário informa data de início e de término
- **THEN** a interface registra o intervalo completo

#### Scenario: Escopo do registro
- **WHEN** o usuário deixa o projeto em branco
- **THEN** a interface indica que o registro se aplica a todos os projetos

#### Scenario: Remoção
- **WHEN** o usuário remove um registro
- **THEN** a interface confirma a intenção antes de excluir

### Requirement: Aviso sobre a ausência de efeito no cálculo
O sistema SHALL informar de forma visível que as datas cadastradas ainda não afetam as simulações.

#### Scenario: Acesso à tela
- **WHEN** o usuário acessa a tela de datas não letivas
- **THEN** a interface exibe aviso permanente informando que os dados são registrados para uso futuro e ainda não impactam o cálculo dos calendários

#### Scenario: Confirmação de cadastro
- **WHEN** o usuário cadastra ou importa uma data não letiva
- **THEN** a confirmação reforça que o registro ainda não altera os resultados das simulações

### Requirement: Sinalização de datas sem efeito prático
O sistema SHALL indicar os registros que caem em dias que já não têm aula.

#### Scenario: Registro em fim de semana ou sexta-feira
- **WHEN** um registro cobre apenas sábados, domingos ou sextas-feiras
- **THEN** a interface o sinaliza como sem efeito prático, já que esses dias não recebem turma regular

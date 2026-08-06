## MODIFIED Requirements

### Requirement: Parse de campos multivalorados
O sistema SHALL interpretar os campos `turnos`, `dias_semana` e `tipologias` como listas separadas por ponto e vírgula.

#### Scenario: Instrutor com múltiplos slots de turno
- **WHEN** uma linha traz `turnos = manha_1;manha_2;noite`
- **THEN** o sistema persiste os três slots para o instrutor, sem exigir nem interpretar carga horária

#### Scenario: Espaços em torno dos separadores
- **WHEN** uma linha traz `tipologias = Programação ; Pixel Art`
- **THEN** o sistema remove os espaços das extremidades e registra as duas tipologias corretamente

### Requirement: Validação linha a linha com relatório de erros
O sistema SHALL validar cada linha isoladamente e importar as válidas, reportando as rejeitadas sem abortar a operação.

#### Scenario: Planilha com linhas válidas e inválidas
- **WHEN** uma planilha de dez linhas contém duas linhas inválidas
- **THEN** o sistema importa as oito válidas e retorna um relatório listando as duas rejeitadas, com o número da linha e o motivo de cada rejeição

#### Scenario: Instrutor sem tipologia
- **WHEN** uma linha traz o campo `tipologias` vazio
- **THEN** o sistema rejeita a linha, pois um instrutor sem tipologia não gera nenhuma oferta

#### Scenario: Slot de turno inválido
- **WHEN** uma linha traz um turno fora de `manha_1`, `manha_2`, `tarde_1`, `tarde_2` e `noite`
- **THEN** o sistema rejeita a linha informando o valor inválido encontrado e os valores aceitos

#### Scenario: Dia da semana fora da faixa
- **WHEN** uma linha traz um dia da semana fora da faixa de 2 a 6
- **THEN** o sistema rejeita a linha informando o valor inválido

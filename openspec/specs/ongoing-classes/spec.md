# ongoing-classes Specification

## Purpose
TBD - created by archiving change add-data-ingestion. Update Purpose after archive.
## Requirements
### Requirement: Registro das turmas em andamento
O sistema SHALL registrar as turmas atualmente em execução, com instrutor alocado, tipologia, modalidade, turno e datas de início e término prevista — via importação de planilha ou cadastro direto.

#### Scenario: Importação da situação atual
- **WHEN** a planilha de turmas em andamento é importada com duas turmas
- **THEN** o sistema persiste as duas turmas vinculadas aos respectivos instrutores e tipologias

#### Scenario: Planilha vazia
- **WHEN** a planilha de turmas em andamento é importada sem nenhuma linha de dados
- **THEN** o sistema conclui a importação sem erro, caracterizando o cenário em que nenhuma turma está em curso

#### Scenario: Cadastro direto
- **WHEN** o usuário cadastra uma turma em andamento pela API
- **THEN** o sistema persiste o registro com as mesmas validações da importação

### Requirement: Validação das turmas em andamento
O sistema SHALL validar a coerência de cada turma em andamento contra os dados de instrutores e tipologias já cadastrados.

#### Scenario: Instrutor inexistente
- **WHEN** uma linha referencia um instrutor que não está cadastrado
- **THEN** o sistema rejeita a linha informando o nome não encontrado

#### Scenario: Slot de turno incompatível com o instrutor
- **WHEN** uma linha aloca um instrutor a um slot de turno que não consta em sua disponibilidade
- **THEN** o sistema rejeita a linha informando a incompatibilidade

#### Scenario: Datas inconsistentes
- **WHEN** uma linha traz data de término anterior à data de início
- **THEN** o sistema rejeita a linha informando a inconsistência

#### Scenario: Modalidade inválida
- **WHEN** uma linha traz modalidade fora de `regular_seg_qua`, `regular_ter_qui` e `intensiva_seg_qui`
- **THEN** o sistema rejeita a linha informando os valores aceitos

### Requirement: Aceitação de sobrecarga real
O sistema SHALL aceitar turmas em andamento cujos períodos se sobrepõem no mesmo slot de turno de um instrutor, emitindo alerta em vez de erro.

#### Scenario: Mesmo slot com períodos sobrepostos
- **WHEN** duas turmas em andamento do mesmo instrutor ocupam o mesmo slot com intervalos de datas que se sobrepõem
- **THEN** o sistema importa os registros e emite alerta, pois esse é o retrato do mundo real e não um erro de preenchimento


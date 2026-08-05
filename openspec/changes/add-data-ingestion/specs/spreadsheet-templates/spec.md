## ADDED Requirements

### Requirement: Download de planilhas-modelo
O sistema SHALL disponibilizar, para download, planilhas-modelo em branco com os cabeçalhos esperados por cada tipo de importação.

#### Scenario: Modelo de instrutores
- **WHEN** o usuário solicita o modelo de instrutores
- **THEN** o sistema retorna um arquivo `.xlsx` com os cabeçalhos corretos e uma linha de exemplo preenchida

#### Scenario: Modelo de tipologias
- **WHEN** o usuário solicita o modelo de tipologias
- **THEN** o sistema retorna um arquivo com os cabeçalhos `tipologia`, `carga_horaria_total`, `horas_por_encontro` e `descricao`

#### Scenario: Modelo de turmas em andamento
- **WHEN** o usuário solicita o modelo de turmas em andamento
- **THEN** o sistema retorna um arquivo com os cabeçalhos de instrutor, tipologia, modalidade, turno e datas

#### Scenario: Tipo de modelo desconhecido
- **WHEN** o usuário solicita um modelo para um tipo não suportado
- **THEN** o sistema retorna erro informando os tipos disponíveis

### Requirement: Modelo autoexplicativo
Os modelos SHALL indicar o formato esperado dos campos multivalorados, para que o usuário não precise consultar documentação externa.

#### Scenario: Orientação de preenchimento
- **WHEN** o usuário abre o modelo de instrutores
- **THEN** a linha de exemplo demonstra o uso do ponto e vírgula nos campos de turnos, dias e tipologias

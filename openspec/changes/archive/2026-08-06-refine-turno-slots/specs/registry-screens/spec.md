## MODIFIED Requirements

### Requirement: Edição de instrutor
O sistema SHALL permitir ajustar a disponibilidade e as habilidades de um instrutor sem exigir reimportação da planilha.

#### Scenario: Alteração de disponibilidade
- **WHEN** o usuário altera os slots de turno ou os dias de um instrutor e confirma
- **THEN** a interface persiste a alteração e reflete o novo estado na listagem

#### Scenario: Erro de validação
- **WHEN** a alteração é rejeitada pelo backend
- **THEN** a interface exibe o motivo junto ao campo correspondente, preservando os dados já preenchidos

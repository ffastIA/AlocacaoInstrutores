## MODIFIED Requirements

### Requirement: Cadastro e edição de turma em andamento
O sistema SHALL permitir registrar e ajustar turmas em andamento diretamente pela interface.

#### Scenario: Cadastro manual
- **WHEN** o usuário informa instrutor, tipologia, modalidade, slot de turno e datas, e confirma
- **THEN** a interface persiste a turma e a exibe na listagem

#### Scenario: Slot de turno incompatível com o instrutor
- **WHEN** o usuário seleciona um slot de turno fora da disponibilidade do instrutor escolhido
- **THEN** a interface impede a confirmação e explica a incompatibilidade

#### Scenario: Datas inconsistentes
- **WHEN** o usuário informa data de término anterior à de início
- **THEN** a interface exibe o erro junto ao campo de data

#### Scenario: Remoção de turma
- **WHEN** o usuário remove uma turma em andamento
- **THEN** a interface confirma a intenção antes de excluir e atualiza a listagem

## REMOVED Requirements

### Requirement: Alerta de sobrecarga
**Reason**: capacidade por turno deixou de ser expressa em horas — não há mais "soma de horas acima do declarado" a calcular no cliente. A sobreposição de datas no mesmo slot já é sinalizada pelo backend no momento da importação (ver capacidade `ongoing-classes`), e o formulário manual desta tela nunca teve checagem equivalente.
**Migration**: nenhuma ação do usuário necessária. Sobreposições de slot são reportadas como alerta no relatório de importação, não mais como um indicador calculado nesta tela.

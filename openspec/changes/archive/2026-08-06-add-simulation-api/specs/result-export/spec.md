## ADDED Requirements

### Requirement: Exportação do resultado em planilha
O sistema SHALL exportar o resultado de uma simulação concluída em arquivo de planilha.

#### Scenario: Exportação das turmas sugeridas
- **WHEN** o usuário exporta uma simulação concluída
- **THEN** o sistema gera um arquivo contendo, por turma sugerida, tipologia, instrutor, projeto, modalidade, turno, datas de início e término e carga horária

#### Scenario: Inclusão dos indicadores
- **WHEN** o arquivo é gerado
- **THEN** ele inclui também os KPIs da simulação e os parâmetros do cenário que a produziu

#### Scenario: Exportação de simulação sem turmas
- **WHEN** a simulação concluiu sem nenhuma turma sugerida
- **THEN** o sistema gera o arquivo com os indicadores e nenhuma linha de turma, sem erro

### Requirement: Restrição a simulações concluídas
O sistema SHALL permitir exportação apenas de simulações que concluíram com sucesso.

#### Scenario: Simulação em processamento
- **WHEN** o usuário tenta exportar uma simulação ainda em execução
- **THEN** o sistema recusa a operação informando que a simulação não está concluída

### Requirement: Nome de arquivo identificável
O sistema SHALL nomear o arquivo exportado de forma que identifique a simulação de origem.

#### Scenario: Nomeação do arquivo
- **WHEN** um arquivo é exportado
- **THEN** seu nome contém o identificador ou o nome do cenário e a data da execução

## ADDED Requirements

### Requirement: Persistência em SQLite
O sistema SHALL persistir todos os dados de domínio e o histórico de simulações em um banco SQLite local, reservando arquivos JSON exclusivamente para os parâmetros de cenário.

#### Scenario: Criação do banco na primeira execução
- **WHEN** a aplicação inicia e o arquivo SQLite não existe
- **THEN** o sistema cria o arquivo e aplica todas as migrações, deixando o esquema pronto para uso

#### Scenario: Separação entre dados e configuração
- **WHEN** um cenário de simulação é gravado
- **THEN** seus metadados ficam na tabela `cenarios` no SQLite e seus pesos de objetivo ficam em um arquivo JSON referenciado por `parametros_json_path`

### Requirement: Modelo de projetos e instrutores
O sistema SHALL modelar instrutores vinculados a um projeto, cada um com seus turnos de disponibilidade (e respectiva carga horária), dias da semana disponíveis e tipologias que domina.

#### Scenario: Instrutor com múltiplos turnos e cargas distintas
- **WHEN** um instrutor é gravado com disponibilidade de 4h pela manhã e 3h à noite
- **THEN** o sistema persiste dois registros de turno, cada um com sua própria carga horária, associados ao mesmo instrutor

#### Scenario: Instrutor com múltiplas tipologias
- **WHEN** um instrutor domina Programação e Pixel Art
- **THEN** o sistema persiste dois vínculos na relação N:N entre instrutor e tipologia

#### Scenario: Dias da semana disponíveis
- **WHEN** um instrutor está disponível às segundas e quartas
- **THEN** o sistema persiste os dias `2` e `4` como registros de disponibilidade daquele instrutor

### Requirement: Modelo de tipologias
O sistema SHALL modelar tipologias com nome, carga horária total e horas por encontro.

#### Scenario: Tipologia com carga compatível
- **WHEN** uma tipologia de 40h com 4h por encontro é gravada
- **THEN** o sistema persiste os dois valores, dos quais o número de encontros (10) é derivável

#### Scenario: Nome único
- **WHEN** uma tipologia é gravada com um nome já existente
- **THEN** o sistema rejeita a operação por violação de unicidade

### Requirement: Modelo de turmas em andamento
O sistema SHALL modelar as turmas atualmente em execução, com tipologia, instrutor alocado, modalidade, turno e datas de início e término prevista.

#### Scenario: Turma em andamento persistida
- **WHEN** uma turma em andamento é gravada com instrutor, tipologia, modalidade, turno e datas
- **THEN** o sistema persiste o registro com integridade referencial para instrutor e tipologia

### Requirement: Modelo de datas não letivas
O sistema SHALL modelar intervalos de datas sem aula (feriados, recessos e férias), com vínculo opcional a um projeto.

#### Scenario: Intervalo aplicável a todos os projetos
- **WHEN** uma data não letiva é gravada sem projeto associado
- **THEN** o sistema persiste `projeto_id` nulo, indicando que o intervalo vale para todos os projetos

### Requirement: Modelo de cenários e simulações
O sistema SHALL modelar cenários de simulação (período, escopo de projetos, caminho do JSON de parâmetros) e o histórico de execuções, incluindo turmas sugeridas, seus encontros e os KPIs resultantes.

#### Scenario: Simulação vinculada ao cenário
- **WHEN** uma simulação é executada a partir de um cenário
- **THEN** o sistema persiste a simulação vinculada ao cenário, com status, tempo de execução e status do solver

#### Scenario: Reprodutibilidade do resultado
- **WHEN** uma simulação é concluída
- **THEN** o sistema persiste um snapshot da capacidade de cada instrutor usada naquela execução, de modo que o resultado permaneça auditável mesmo que as turmas em andamento mudem depois

### Requirement: Migrações versionadas
O sistema SHALL gerenciar a evolução do esquema por meio de migrações versionadas, aplicáveis e reversíveis.

#### Scenario: Aplicação das migrações
- **WHEN** o comando de migração é executado em um banco vazio
- **THEN** todas as tabelas do domínio são criadas na ordem correta de dependências

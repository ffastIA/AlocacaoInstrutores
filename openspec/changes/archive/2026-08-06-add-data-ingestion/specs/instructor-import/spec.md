## ADDED Requirements

### Requirement: Importação da planilha de instrutores
O sistema SHALL aceitar upload de planilha `.xlsx` ou `.csv` contendo instrutores e persistir os dados válidos.

#### Scenario: Importação bem-sucedida
- **WHEN** uma planilha válida com três instrutores é enviada
- **THEN** o sistema persiste os três instrutores com seus turnos, dias, tipologias e projeto, e retorna um resumo com a contagem de registros importados

#### Scenario: Reconhecimento de cabeçalhos independente de ordem e acentuação
- **WHEN** a planilha traz as colunas em ordem diferente e com acentos ou maiúsculas (`Nome`, `Dias Semana`, `Tipologias`)
- **THEN** o sistema normaliza os cabeçalhos e localiza as colunas corretamente

#### Scenario: Coluna obrigatória ausente
- **WHEN** a planilha não contém a coluna `tipologias`
- **THEN** o sistema rejeita o arquivo inteiro e informa qual coluna obrigatória está faltando

### Requirement: Parse de campos multivalorados
O sistema SHALL interpretar os campos `turnos`, `carga_horaria_turno`, `dias_semana` e `tipologias` como listas separadas por ponto e vírgula.

#### Scenario: Instrutor com múltiplos turnos e cargas distintas
- **WHEN** uma linha traz `turnos = manha;noite` e `carga_horaria_turno = 4;3`
- **THEN** o sistema persiste 4 horas para o turno da manhã e 3 horas para o turno da noite

#### Scenario: Listas de tamanhos incompatíveis
- **WHEN** uma linha traz `turnos = manha;tarde` e `carga_horaria_turno = 4`
- **THEN** o sistema rejeita a linha informando o desalinhamento entre turnos e cargas horárias, sem inferir valores

#### Scenario: Formato explícito turno:horas
- **WHEN** uma linha traz `turnos = manha:4;tarde:4` sem a coluna `carga_horaria_turno`
- **THEN** o sistema aceita o formato explícito e persiste os turnos com suas cargas horárias

#### Scenario: Espaços em torno dos separadores
- **WHEN** uma linha traz `tipologias = Programação ; Pixel Art`
- **THEN** o sistema remove os espaços das extremidades e registra as duas tipologias corretamente

### Requirement: Derivação automática de tipologias e projetos
O sistema SHALL criar automaticamente os registros de tipologia e de projeto encontrados na planilha de instrutores.

#### Scenario: Tipologia inédita
- **WHEN** a planilha traz um instrutor que domina uma tipologia ainda não cadastrada
- **THEN** o sistema cria a tipologia no catálogo, marcada como pendente de configuração de carga horária

#### Scenario: Projeto inédito
- **WHEN** a planilha traz um instrutor de um projeto ainda não cadastrado
- **THEN** o sistema cria o projeto automaticamente

#### Scenario: Tipologia já existente
- **WHEN** a planilha traz uma tipologia já cadastrada e configurada
- **THEN** o sistema reutiliza o registro existente sem sobrescrever sua carga horária

### Requirement: Tratamento do dia 6 como reposição
O sistema SHALL aceitar o dia 6 (sexta-feira) na disponibilidade do instrutor, registrando-o como capacidade de reposição que nunca recebe turma regular.

#### Scenario: Instrutor disponível de segunda a sexta
- **WHEN** uma linha traz `dias_semana = 2;3;4;5;6`
- **THEN** o sistema persiste os cinco dias e sinaliza que o dia 6 conta apenas como capacidade de reposição

### Requirement: Validação linha a linha com relatório de erros
O sistema SHALL validar cada linha isoladamente e importar as válidas, reportando as rejeitadas sem abortar a operação.

#### Scenario: Planilha com linhas válidas e inválidas
- **WHEN** uma planilha de dez linhas contém duas linhas inválidas
- **THEN** o sistema importa as oito válidas e retorna um relatório listando as duas rejeitadas, com o número da linha e o motivo de cada rejeição

#### Scenario: Instrutor sem tipologia
- **WHEN** uma linha traz o campo `tipologias` vazio
- **THEN** o sistema rejeita a linha, pois um instrutor sem tipologia não gera nenhuma oferta

#### Scenario: Turno inválido
- **WHEN** uma linha traz um turno fora de `manha`, `tarde` e `noite`
- **THEN** o sistema rejeita a linha informando o valor inválido encontrado

#### Scenario: Dia da semana fora da faixa
- **WHEN** uma linha traz um dia da semana fora da faixa de 2 a 6
- **THEN** o sistema rejeita a linha informando o valor inválido

### Requirement: Reimportação de instrutores
O sistema SHALL permitir reimportar a planilha de instrutores para refletir atualizações, sem duplicar registros.

#### Scenario: Instrutor já existente com dados alterados
- **WHEN** a planilha é reimportada com a disponibilidade de um instrutor alterada
- **THEN** o sistema atualiza turnos, dias e tipologias daquele instrutor em vez de criar um registro duplicado

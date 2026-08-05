## ADDED Requirements

### Requirement: Decisão de abertura por candidata
O sistema SHALL representar cada turma candidata por uma variável booleana de decisão, cujo valor indica se a turma é aberta.

#### Scenario: Solução retornada
- **WHEN** o solver conclui a busca
- **THEN** o sistema retorna a lista de turmas a abrir, cada uma com instrutor, tipologia, turno, modalidade, datas de início e término e o calendário de encontros

#### Scenario: Nenhuma turma viável
- **WHEN** nenhum instrutor tem capacidade livre no período
- **THEN** o sistema retorna uma solução vazia sem erro, indicando que não há oportunidade de abertura

### Requirement: Respeito à capacidade horária por turno
O sistema SHALL garantir que as horas alocadas a um instrutor em um dia e turno nunca ultrapassem sua capacidade horária declarada naquele turno.

#### Scenario: Duas turmas curtas no mesmo turno
- **WHEN** um instrutor tem 4 horas de capacidade em um turno e duas tipologias de 2 horas por encontro
- **THEN** o solver pode alocar as duas turmas no mesmo turno e dia

#### Scenario: Capacidade insuficiente para acumular
- **WHEN** um instrutor tem 3 horas de capacidade no turno da noite e duas tipologias de 2 horas por encontro
- **THEN** o solver aloca no máximo uma das turmas naquele turno e dia

#### Scenario: Capacidade consumida por turma em andamento
- **WHEN** uma turma em andamento já ocupa integralmente a capacidade de um instrutor em um turno
- **THEN** o solver não aloca nenhuma turma sugerida naquele turno enquanto a turma em andamento não terminar

### Requirement: Teto de turmas por dia
O sistema SHALL limitar a quatro o número de turmas de um mesmo instrutor em um mesmo dia, contando as turmas em andamento.

#### Scenario: Limite respeitado
- **WHEN** um instrutor já tem quatro turmas em um dia
- **THEN** o solver não aloca uma quinta turma naquele dia

#### Scenario: Turmas em andamento contam para o limite
- **WHEN** um instrutor tem três turmas em andamento em um dia
- **THEN** o solver aloca no máximo mais uma turma sugerida naquele dia

### Requirement: Aproveitamento de capacidade residual
O sistema SHALL permitir que um instrutor assuma nova turma sem ter encerrado as atuais, desde que haja dia e turno com capacidade livre.

#### Scenario: Turno livre durante turma em andamento
- **WHEN** um instrutor tem turma em andamento pela manhã e disponibilidade livre à tarde
- **THEN** o solver pode alocar uma turma sugerida no turno da tarde antes do término da turma da manhã

### Requirement: Encadeamento de turmas ao longo do período
O sistema SHALL simular a sequência completa de aberturas no período, permitindo que um instrutor receba turmas sucessivas conforme sua capacidade se libera.

#### Scenario: Turmas sucessivas
- **WHEN** o período simulado comporta três turmas consecutivas de uma tipologia no mesmo turno de um instrutor
- **THEN** o solver pode alocar as três, cada uma iniciando após o término da anterior

#### Scenario: Sem sobreposição indevida
- **WHEN** duas turmas sugeridas são alocadas ao mesmo instrutor no mesmo turno
- **THEN** seus calendários de encontros não excedem a capacidade daquele turno em nenhuma data

### Requirement: Objetivo composto configurável
O sistema SHALL otimizar uma função objetivo combinando quatro termos ponderados: aproveitamento da capacidade, antecipação das datas de início, equilíbrio de carga entre instrutores e equilíbrio entre tipologias.

#### Scenario: Peso exclusivo em aproveitamento
- **WHEN** todo o peso é atribuído ao aproveitamento
- **THEN** o solver maximiza as horas de formação entregues, ainda que a distribuição entre instrutores e tipologias fique desigual

#### Scenario: Peso em equilíbrio de tipologias
- **WHEN** um peso relevante é atribuído ao equilíbrio entre tipologias
- **THEN** o solver distribui as turmas dos instrutores multi-tipologia entre as tipologias possíveis, em vez de concentrá-las em uma só

#### Scenario: Peso em antecipação
- **WHEN** um peso relevante é atribuído à antecipação
- **THEN** o solver prefere semanas de início mais cedo entre as soluções de aproveitamento equivalente

#### Scenario: Normalização dos termos
- **WHEN** os quatro termos são combinados
- **THEN** cada um é normalizado antes da ponderação, de modo que os pesos reflitam a importância pretendida e não a escala das grandezas

### Requirement: Limites de execução do solver
O sistema SHALL respeitar limite de tempo configurável e retornar a melhor solução encontrada, informando o status da busca.

#### Scenario: Solução ótima dentro do tempo
- **WHEN** o solver prova a otimalidade antes do limite de tempo
- **THEN** o sistema retorna a solução indicando status ótimo

#### Scenario: Tempo esgotado
- **WHEN** o limite de tempo é atingido com uma solução viável encontrada
- **THEN** o sistema retorna essa solução indicando que o tempo se esgotou e informando a distância estimada do ótimo

### Requirement: Determinismo da simulação
O sistema SHALL produzir o mesmo resultado ao ser executado duas vezes sobre os mesmos dados e parâmetros.

#### Scenario: Execuções repetidas
- **WHEN** a mesma simulação é executada duas vezes com os mesmos dados, pesos e semente
- **THEN** o conjunto de turmas sugeridas é idêntico

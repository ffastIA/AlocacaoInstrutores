# allocation-solver Specification

## Purpose
TBD - created by archiving change add-class-opening-simulator. Update Purpose after archive.
## Requirements
### Requirement: Decisão de abertura por candidata
O sistema SHALL representar cada turma candidata por uma variável booleana de decisão, cujo valor indica se a turma é aberta.

#### Scenario: Solução retornada
- **WHEN** o solver conclui a busca
- **THEN** o sistema retorna a lista de turmas a abrir, cada uma com instrutor, tipologia, turno, modalidade, datas de início e término e o calendário de encontros

#### Scenario: Nenhuma turma viável
- **WHEN** nenhum instrutor tem capacidade livre no período
- **THEN** o sistema retorna uma solução vazia sem erro, indicando que não há oportunidade de abertura

### Requirement: Respeito à capacidade horária por turno
O sistema SHALL garantir que cada slot de turno (`manha_1`, `manha_2`, `tarde_1`, `tarde_2`, `noite`) de um instrutor tenha no máximo uma turma ativa por vez.

#### Scenario: Slot livre em um dia
- **WHEN** um instrutor tem um slot sem nenhuma turma naquele dia
- **THEN** o solver pode alocar uma turma candidata naquele slot e dia

#### Scenario: Slot já ocupado
- **WHEN** um slot de um instrutor já tem uma turma (em andamento ou já selecionada pelo solver) naquele dia
- **THEN** o solver não aloca nenhuma outra turma candidata naquele mesmo slot e dia

#### Scenario: Capacidade consumida por turma em andamento
- **WHEN** uma turma em andamento já ocupa um slot de um instrutor
- **THEN** o solver não aloca nenhuma turma sugerida naquele slot enquanto a turma em andamento não terminar

### Requirement: Aproveitamento de capacidade residual
O sistema SHALL permitir que um instrutor assuma nova turma sem ter encerrado as atuais, desde que haja um slot livre em algum dia da modalidade.

#### Scenario: Slot livre durante turma em andamento
- **WHEN** um instrutor tem turma em andamento em `manha_1` e o slot `tarde_1` está livre
- **THEN** o solver pode alocar uma turma sugerida em `tarde_1` antes do término da turma em `manha_1`

### Requirement: Encadeamento de turmas ao longo do período
O sistema SHALL simular a sequência completa de aberturas no período, permitindo que um instrutor receba turmas sucessivas no mesmo slot conforme sua capacidade se libera.

#### Scenario: Turmas sucessivas
- **WHEN** o período simulado comporta três turmas consecutivas de uma tipologia no mesmo slot de um instrutor
- **THEN** o solver pode alocar as três, cada uma iniciando após o término da anterior

#### Scenario: Sem sobreposição indevida
- **WHEN** duas turmas sugeridas são alocadas ao mesmo instrutor no mesmo slot
- **THEN** seus calendários de encontros não se sobrepõem em nenhuma data

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


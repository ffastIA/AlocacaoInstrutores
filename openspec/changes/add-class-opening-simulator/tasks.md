## 1. Gerador de calendário

- [ ] 1.1 Definir os padrões de dias das modalidades `regular_seg_qua`, `regular_ter_qui` e `intensiva_seg_qui`, nenhum incluindo sexta-feira
- [ ] 1.2 Implementar `gerador_encontros.py` produzindo a sequência de encontros a partir de tipologia, modalidade e semana de início
- [ ] 1.3 Derivar o número de encontros da carga horária total dividida pelas horas por encontro
- [ ] 1.4 Calcular a data de término como a data do último encontro
- [ ] 1.5 Testar determinismo, ausência de sextas e preservação da carga horária total

## 2. Enumerador de candidatas

- [ ] 2.1 Implementar `gerador_candidatas.py` combinando instrutor, tipologia, turno, modalidade e semana de início
- [ ] 2.2 Podar por tipologia não dominada e por turno indisponível
- [ ] 2.3 Podar por incompatibilidade entre o padrão de dias da modalidade e os dias disponíveis do instrutor
- [ ] 2.4 Podar quando as horas por encontro da tipologia excedem a capacidade do instrutor naquele turno
- [ ] 2.5 Podar candidatas cuja turma ultrapassaria o fim do período simulado
- [ ] 2.6 Aplicar o escopo de projetos, respeitando a flag de compartilhamento
- [ ] 2.7 Pré-computar, por candidata, o mapa de horas por data e turno
- [ ] 2.8 Instrumentar a contagem de candidatas geradas e podadas, para diagnóstico de escala

## 3. Modelo CP-SAT

- [ ] 3.1 Criar uma variável booleana por candidata
- [ ] 3.2 Implementar a restrição de capacidade horária por instrutor, data e turno
- [ ] 3.3 Somar o consumo das turmas em andamento nas restrições de capacidade
- [ ] 3.4 Implementar a restrição de teto de quatro turmas por instrutor e dia, contando as em andamento
- [ ] 3.5 Implementar o termo de aproveitamento: soma das horas de formação das turmas abertas
- [ ] 3.6 Implementar o termo de antecipação favorecendo semanas de início mais cedo
- [ ] 3.7 Implementar o termo de equilíbrio de carga como range da utilização percentual entre instrutores
- [ ] 3.8 Implementar o termo de equilíbrio entre tipologias como range da contagem de turmas por tipologia
- [ ] 3.9 Normalizar os quatro termos e combiná-los com os pesos do cenário
- [ ] 3.10 Aplicar limite de tempo, número de workers e semente fixa para determinismo
- [ ] 3.11 Extrair a solução para uma estrutura de turmas sugeridas com seus calendários

## 4. Métricas

- [ ] 4.1 Calcular o percentual de ociosidade agregada
- [ ] 4.2 Calcular a primeira data livre de cada instrutor
- [ ] 4.3 Calcular horas alocadas, horas disponíveis e utilização percentual por instrutor
- [ ] 4.4 Calcular a distribuição de turmas por tipologia e os índices de equilíbrio
- [ ] 4.5 Calcular o leque de tipologias possíveis por data, com os instrutores que as sustentam
- [ ] 4.6 Calcular a capacidade de reposição disponível às sextas-feiras
- [ ] 4.7 Reunir os metadados de execução: total de turmas, horas de formação, valor do objetivo, status e tempo do solver

## 5. Testes de restrição

- [ ] 5.1 Instrutor com dias `2;4` nunca recebe turma intensiva
- [ ] 5.2 Tipologia de 4 horas por encontro nunca é alocada em turno com 3 horas de capacidade
- [ ] 5.3 Duas tipologias de 2 horas cabem juntas em turno de 4 horas, mas não em turno de 3 horas
- [ ] 5.4 Teto de quatro turmas por dia respeitado, contando as turmas em andamento
- [ ] 5.5 Nenhum encontro cai em sexta-feira
- [ ] 5.6 Instrutor com turma em andamento pela manhã recebe sugestão à tarde, mas não no turno ocupado
- [ ] 5.7 Nenhuma tipologia fora da união das habilidades dos instrutores do escopo é sugerida
- [ ] 5.8 Compartilhamento desligado impede turma de instrutor de outro projeto
- [ ] 5.9 Encadeamento: instrutor livre a partir de determinada data recebe turmas sucessivas, não apenas a primeira
- [ ] 5.10 Duas execuções com os mesmos dados e semente produzem resultado idêntico

## 6. Testes de objetivo

- [ ] 6.1 Peso exclusivo em aproveitamento maximiza as horas de formação entregues
- [ ] 6.2 Peso relevante em equilíbrio de tipologias distribui as turmas de instrutores multi-tipologia
- [ ] 6.3 Peso relevante em antecipação prefere inícios mais cedo entre soluções equivalentes
- [ ] 6.4 Alterar apenas a escala de um termo, mantendo os pesos, não altera a solução — confirmando a normalização

## 7. Cenário de negócio e benchmark

- [ ] 7.1 Reproduzir o caso de referência: instrutor que encerra em 30/08 dominando Pixel Art e Programação gera oportunidades dessas duas tipologias a partir de 31/08, e nenhuma de Robótica
- [ ] 7.2 Criar script em `backend/scripts/` que executa a simulação com dados sintéticos e imprime o resultado
- [ ] 7.3 Executar benchmark com 60 instrutores e 35 semanas, medindo tempo e número de candidatas
- [ ] 7.4 Registrar o resultado do benchmark e decidir se alguma estratégia de poda adicional é necessária

## Context

Este é o núcleo do sistema. As turmas são **saída**, não entrada: não existe uma lista de turmas a alocar, e sim um conjunto de instrutores com capacidade e habilidades, a partir do qual o sistema deriva o que é possível abrir.

Escala alvo: 20 a 60 instrutores, horizonte de aproximadamente 35 semanas. O motor é construído isolado da API para permitir validação com dados sintéticos e medição de performance antes de qualquer acoplamento.

## Goals / Non-Goals

**Goals:**
- Produzir o pipeline completo de aberturas ao longo do período, não apenas a próxima liberação
- Nunca violar as restrições rígidas de capacidade
- Objetivo composto configurável, permitindo comparar cenários com prioridades diferentes
- Executar dentro de um limite de tempo aceitável no teto de escala

**Non-Goals:**
- Exposição via HTTP (change `add-simulation-api`)
- Consideração de datas não letivas (adiada por decisão de escopo)
- Deslocamento geográfico entre locais presenciais
- Revezamento de instrutores dentro de uma mesma turma

## Decisions

### Enumerar candidatas em vez de modelar turmas abstratas
Uma candidata é a tupla instrutor × tipologia × turno × modalidade × semana de início. Como turno e modalidade são fixos por candidata, o calendário de encontros fica **totalmente determinado** e é pré-computado fora do solver — o CP-SAT recebe apenas coeficientes numéricos.

*Alternativa considerada:* variáveis inteiras de data de início com restrições de precedência. Descartada porque tornaria o calendário dependente de variáveis de decisão, exigindo restrições reificadas para cada encontro e inflando o modelo muito além do ganho.

### Poda na criação, não por restrição
Combinações inviáveis (tipologia não dominada, turno indisponível, dias incompatíveis, horas por encontro acima da capacidade) simplesmente **não geram variável**, em vez de gerar variável fixada em zero. Reduz o modelo em uma ordem de grandeza antes de o solver começar.

### Capacidade por (instrutor, data, turno) — é o que produz o encadeamento
Esta é a decisão central. A restrição não é um flag global de "instrutor ocupado", e sim um balde de horas por dia e turno. Uma candidata consome capacidade **apenas nas datas dos seus próprios encontros**. Consequências diretas:

- **Capacidade residual**: instrutor com turma pela manhã pode receber turma à tarde antes de encerrar a primeira
- **Encadeamento**: quando uma turma sugerida termina, a capacidade se libera e candidatas com início posterior tornam-se viáveis
- Como todas as candidatas de todas as semanas coexistem no modelo, o solver escolhe a **sequência inteira de uma vez**, avaliando o encadeamento globalmente em vez de decidir turma a turma

### Turno como balde de horas, não como slot único
O limite de 4 turmas por dia só é coerente com 3 turnos se mais de uma turma couber num turno. Modelar o turno pela sua capacidade horária resolve isso: duas turmas de 2 horas cabem num turno de 4 horas, mas não num de 3. *Limitação aceita:* a v1 não representa horário de início dentro do turno, então não distingue duas turmas de 2 horas sequenciais de duas simultâneas. Aceitável porque o dado de horário não existe nas entradas.

### Turmas em andamento como constantes, não variáveis
Elas já estão decididas. Entram nas restrições como consumo fixo de capacidade até sua data de término. Isso é o que faz a disponibilidade ser progressiva por instrutor, sem precisar de uma "data de liberação" calculada à parte.

### Sem variável de gap
Diferente de um problema de cobertura, aqui não há turma obrigatória a atender. Uma candidata não escolhida simplesmente não vira turma. O modelo é sempre viável — a solução vazia é válida e significa "nenhuma oportunidade no período".

### Normalização obrigatória dos termos do objetivo
Os quatro termos têm escalas incompatíveis: horas-turma na casa dos milhares, utilização percentual em escala 0–1000, contagem de turmas em dezenas. Sem normalizar, um peso de 0,2 num termo de escala grande domina um peso de 0,8 num termo de escala pequena. Os fatores de normalização são persistidos junto ao cenário para que comparações entre simulações sejam válidas.

### Equilíbrio por range (máximo menos mínimo)
Para carga e tipologias, usa-se `AddMaxEquality`/`AddMinEquality` sobre utilização percentual — não sobre horas brutas, que penalizariam injustamente instrutores com menor capacidade declarada. *Alternativa considerada:* desvio absoluto em relação à média, que é mais suave mas exige mais variáveis auxiliares. Se o range se mostrar caro no benchmark, é a substituição natural.

## Risks / Trade-offs

- **Explosão combinatória** — 60 instrutores × ~3 tipologias × 3 turnos × 3 modalidades × 35 semanas ≈ 170 mil booleanos, e o número cresce linearmente com o período simulado → mitigações em ordem de preferência: restringir semanas de início a um grid quinzenal ou mensal, limitar modalidades por cenário, resolver em janelas deslizantes com encadeamento entre janelas. O benchmark no teto de escala decide se alguma é necessária
- **Custo de `AddMaxEquality` sobre utilização percentual** → medir isoladamente; substituir por desvio absoluto se dominar o tempo de solução
- **Solução ótima porém contraintuitiva** para a equipe de mobilização → mitigado pelos pesos configuráveis e pelo relatório que explica a composição do objetivo
- **Ausência de horário dentro do turno** pode gerar sugestão inexequível na prática → documentado como limitação conhecida; o dado necessário não existe nas entradas atuais

## Migration Plan

Não aplicável — código novo, sem estado a migrar.

## Open Questions

- O benchmark confirmará se a granularidade semanal de início é sustentável ou se é preciso adotar grid quinzenal
- Definir a semente do solver a ser usada para garantir determinismo entre execuções
- Avaliar se o termo de antecipação deve ser linear na semana ou penalizar mais fortemente os inícios tardios

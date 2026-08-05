## Why

Este é o núcleo do sistema. Hoje a equipe de mobilização não consegue responder "a partir de que data posso divulgar uma turma de Robótica?" — a resposta depende de quando cada instrutor libera capacidade, e cada instrutor domina um conjunto diferente de tipologias.

A lógica é **dirigida pela oferta**: tem instrutor com capacidade livre? Quais tipologias ele domina? Essas são as turmas possíveis. Não há meta de demanda por tipologia — o sistema mostra o que é viável abrir, e a equipe decide o que abrir de fato.

Construir o motor isolado da API permite validar as regras com dados sintéticos e medir performance antes de acoplar qualquer coisa.

## What Changes

- **Gerador de calendário**: dada tipologia, modalidade e semana de início, produz a sequência determinística de encontros (data, turno, horas), nunca em sextas-feiras
- **Enumerador de candidatas**: gera as combinações viáveis de instrutor × tipologia × turno × modalidade × semana de início, podando na origem tudo que é inelegível
- **Modelo CP-SAT** com uma variável booleana por candidata e as restrições rígidas de capacidade horária por turno, teto de 4 turmas/dia, dias e turnos do instrutor, consumo de capacidade pelas turmas em andamento e escopo de projetos
- **Objetivo composto** de quatro termos normalizados e ponderados: aproveitamento, antecipação das datas de início, equilíbrio de carga entre instrutores e equilíbrio entre tipologias
- **Simulação em pipeline**: o motor encadeia turmas sucessivas ao longo de todo o período, não apenas a próxima liberação de cada instrutor
- **Cálculo de KPIs**: ociosidade, primeira data livre por instrutor, distribuição por tipologia, índices de equilíbrio
- Suíte de testes com cenários sintéticos de resposta conhecida e benchmark no teto de escala

## Capabilities

### New Capabilities
- `class-calendar`: geração determinística do calendário de encontros de uma turma
- `candidate-generation`: enumeração e poda das turmas candidatas
- `allocation-solver`: modelo CP-SAT com restrições rígidas e objetivo composto configurável
- `simulation-metrics`: cálculo dos indicadores de resultado da simulação

### Modified Capabilities
Nenhuma — todas as capacidades são novas.

## Impact

- **Novo**: `backend/app/services/calendario/gerador_encontros.py`
- **Novo**: `backend/app/services/solver/{gerador_candidatas,cp_sat_model,metricas}.py`
- **Novo**: `backend/scripts/` para execução isolada e benchmark
- **Dependência**: `ortools` (já adicionada em `setup-backend-foundation`)
- **Consome**: instrutores, tipologias e turmas em andamento de `add-data-ingestion`
- **Não usa**: as datas não letivas de `add-non-teaching-dates`, por decisão explícita de escopo
- **Bloqueia**: `add-simulation-api` expõe este motor via HTTP

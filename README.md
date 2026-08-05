# AlocacaoInstrutores

Sistema para escalonamento das turmas e instrutores.

## Sobre

Ferramenta de simulação que responde **a partir de que data é possível abrir turma de cada tipologia**, com base na disponibilidade e nas habilidades dos instrutores.

A lógica é dirigida pela oferta: tem instrutor com capacidade livre? Quais tipologias ele domina? Essas são as turmas possíveis. As turmas são **saída** da simulação, não entrada — o sistema sugere o que pode ser aberto, e a equipe de mobilização decide o que abrir.

## Stack

- **Backend**: Python, FastAPI, SQLite
- **Otimização**: Google OR-Tools (CP-SAT)
- **Frontend**: React, TypeScript
- **Especificação**: [OpenSpec](https://github.com/Fission-AI/OpenSpec)

## Estrutura

```
backend/          API FastAPI e motor de simulação
frontend/         Interface React
data/             Banco SQLite e cenários em JSON
openspec/         Especificações das mudanças
```

## Desenvolvimento

O projeto é especificado com OpenSpec. As mudanças planejadas estão em `openspec/changes/`:

| Change | Escopo |
|---|---|
| `setup-backend-foundation` | FastAPI, SQLite e modelo de dados |
| `add-data-ingestion` | Importação de planilhas e cadastros |
| `add-non-teaching-dates` | Calendário de feriados e recessos |
| `add-class-opening-simulator` | Motor CP-SAT de simulação |
| `add-simulation-api` | Endpoints de cenários e simulações |
| `setup-frontend-foundation` | Base React e design system |
| `add-frontend-data-screens` | Telas de dados |
| `add-frontend-simulation-screens` | Telas de simulação |

Para ver o status: `openspec list`

## Why

A equipe de mobilização já mantém os dados de instrutores em planilha. Exigir digitação manual de 20 a 60 instrutores — cada um com múltiplos turnos, dias e tipologias — inviabilizaria o uso da ferramenta.

Além disso, o catálogo de tipologias **não existe independentemente**: uma tipologia só é ofertável porque algum instrutor a domina. Derivar o catálogo da própria planilha de instrutores elimina uma etapa de cadastro e garante que catálogo e habilidades nunca divirjam.

## What Changes

- Importação da planilha de **instrutores** (`.xlsx`/`.csv`), com parse dos campos multivalorados separados por `;` (turnos, cargas horárias, dias da semana, tipologias)
- **Derivação automática** do catálogo de tipologias e da lista de projetos a partir da planilha de instrutores
- Importação da planilha de **tipologias**, que apenas completa carga horária total e horas por encontro das tipologias já derivadas
- Importação da planilha de **turmas em andamento**, que retrata a situação atual das alocações
- Relatório de validação linha a linha: cada linha rejeitada informa o número da linha e o motivo, sem abortar a importação inteira
- Download de **planilhas-modelo** em branco com os cabeçalhos corretos
- CRUD de projetos, tipologias, instrutores e turmas em andamento para ajustes pontuais fora da importação

## Capabilities

### New Capabilities
- `instructor-import`: importação e parse da planilha de instrutores, com derivação de tipologias e projetos
- `typology-catalog`: gestão do catálogo de tipologias e sua configuração de carga horária
- `ongoing-classes`: registro das turmas atualmente em execução
- `spreadsheet-templates`: geração de planilhas-modelo para download

### Modified Capabilities
Nenhuma — todas as capacidades são novas.

## Impact

- **Novo**: `backend/app/services/importacao/` (parsers e validadores)
- **Novo**: `backend/app/api/` com as rotas de importação e os CRUDs
- **Novo**: `backend/app/schemas/` com os modelos Pydantic de request e response
- **Usa**: o esquema de dados definido em `setup-backend-foundation`
- **Bloqueia**: `add-class-opening-simulator` precisa desses dados para enumerar candidatas

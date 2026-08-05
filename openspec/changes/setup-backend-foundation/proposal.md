## Why

O sistema de simulação de abertura de turmas ainda não existe — o repositório está vazio. Antes de qualquer regra de negócio, é preciso estabelecer o esqueleto do backend: aplicação FastAPI, banco SQLite, modelo de dados completo e infraestrutura de migração. Todas as demais changes dependem desta base.

Fazer isso como uma change isolada evita que o esquema de dados seja definido aos pedaços por cada funcionalidade, o que geraria migrações redundantes e inconsistências entre tabelas que se relacionam (instrutores ↔ tipologias ↔ turmas ↔ simulações).

## What Changes

- Cria a estrutura de pastas do backend (`backend/app/{api,core,models,schemas,services,db}`)
- Adiciona FastAPI, SQLAlchemy, Alembic e OR-Tools como dependências
- Define o **modelo de dados completo** do domínio em SQLAlchemy: projetos, instrutores (com turnos, dias e tipologias), tipologias, turmas em andamento, datas não letivas, cenários, simulações e resultados
- Configura o SQLite como banco local em `data/`, com migração inicial via Alembic
- Expõe endpoint de healthcheck e habilita CORS para o frontend
- Define configuração por variáveis de ambiente (caminho do banco, diretório de cenários JSON, limites do solver)
- **Sem autenticação** — o sistema é aberto por decisão de produto

## Capabilities

### New Capabilities
- `backend-foundation`: estrutura da aplicação FastAPI, configuração, ciclo de vida e healthcheck
- `data-model`: esquema relacional completo do domínio em SQLite, com migrações versionadas

### Modified Capabilities
Nenhuma — este é o primeiro change do projeto.

## Impact

- **Novo**: todo o diretório `backend/`
- **Novo**: diretório `data/` para o arquivo SQLite e os JSONs de cenário
- **Dependências**: `fastapi`, `uvicorn`, `sqlalchemy`, `alembic`, `pydantic-settings`, `ortools`, `openpyxl`, `pytest`
- **Bloqueia**: todas as demais changes do projeto dependem deste esquema de dados

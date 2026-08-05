# Backend — AlocacaoInstrutores

API FastAPI e motor de simulação de abertura de turmas.

## Requisitos

- Python 3.11 ou superior

## Instalação

A partir de `backend/`:

```bash
python -m venv .venv
```

Ative o ambiente virtual:

```bash
# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# Windows (Git Bash)
source .venv/Scripts/activate

# Linux / macOS
source .venv/bin/activate
```

Instale as dependências, incluindo as de desenvolvimento:

```bash
pip install -e ".[dev]"
```

## Execução

```bash
uvicorn app.main:app --reload
```

A API sobe em `http://localhost:8000`:

- `http://localhost:8000/docs` — documentação interativa
- `http://localhost:8000/health` — verificação de saúde

As migrações pendentes são aplicadas automaticamente na inicialização, criando o banco se ainda não existir.

## Configuração

Todas as variáveis têm padrão adequado para execução local — a aplicação sobe sem nenhuma configuração.

| Variável | Padrão | Descrição |
|---|---|---|
| `DATABASE_URL` | `sqlite:///data/alocacao.db` | Caminho do banco SQLite |
| `CENARIOS_DIR` | `data/cenarios` | Diretório dos JSONs de parâmetros de cenário |
| `CORS_ORIGINS` | `http://localhost:5173,http://localhost:3000` | Origens permitidas, separadas por vírgula |
| `SOLVER_TIME_LIMIT_SEG` | `180` | Limite de tempo do solver, em segundos |
| `SOLVER_NUM_WORKERS` | `8` | Threads paralelas do solver |
| `SOLVER_GAP_RELATIVO` | `0.02` | Distância relativa do ótimo aceita |
| `SOLVER_SEED` | `42` | Semente que garante o determinismo entre execuções |

Os caminhos relativos são resolvidos a partir da raiz do repositório, não do diretório de trabalho.

## Migrações

O esquema é versionado com Alembic:

```bash
alembic upgrade head      # aplica as migrações pendentes
alembic downgrade -1      # reverte a última migração
alembic revision --autogenerate -m "descricao"
```

## Testes

```bash
pytest
```

Os testes usam banco em memória e não tocam o arquivo SQLite de desenvolvimento.

## Estrutura

```
app/
  api/         Rotas HTTP
  core/        Configuração
  db/          Sessão e base declarativa
  models/      Modelos SQLAlchemy e enums
  schemas/     Modelos Pydantic
  services/    Regras de negócio, importação e solver
alembic/       Migrações versionadas
tests/
```

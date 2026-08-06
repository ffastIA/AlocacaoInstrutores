# backend-foundation Specification

## Purpose
TBD - created by archiving change setup-backend-foundation. Update Purpose after archive.
## Requirements
### Requirement: Aplicação FastAPI inicializável
O sistema SHALL expor uma aplicação FastAPI que inicializa sem erros e serve documentação interativa em `/docs`.

#### Scenario: Inicialização bem-sucedida
- **WHEN** o servidor é iniciado com `uvicorn app.main:app`
- **THEN** a aplicação sobe sem erros e `/docs` retorna a interface Swagger com os endpoints registrados

#### Scenario: Healthcheck
- **WHEN** um cliente faz `GET /health`
- **THEN** o sistema retorna HTTP 200 com o status da aplicação e a confirmação de que o banco está acessível

### Requirement: Acesso sem autenticação
O sistema SHALL permitir acesso a todos os endpoints sem credenciais, sem cadastro de usuários e sem controle de permissões.

#### Scenario: Requisição sem credenciais
- **WHEN** um cliente faz uma requisição a qualquer endpoint sem cabeçalho de autenticação
- **THEN** o sistema processa a requisição normalmente e nunca retorna HTTP 401 ou 403

### Requirement: Configuração por variáveis de ambiente
O sistema SHALL ler sua configuração de variáveis de ambiente, com valores padrão adequados para execução local.

#### Scenario: Execução sem variáveis definidas
- **WHEN** a aplicação é iniciada sem nenhuma variável de ambiente definida
- **THEN** o sistema usa os padrões (`data/alocacao.db` para o banco e `data/cenarios/` para os JSONs de cenário) e inicializa normalmente

#### Scenario: Sobrescrita do caminho do banco
- **WHEN** a variável `DATABASE_URL` aponta para outro arquivo SQLite
- **THEN** a aplicação usa esse arquivo em vez do padrão

### Requirement: CORS habilitado para o frontend
O sistema SHALL aceitar requisições cross-origin do frontend React em desenvolvimento.

#### Scenario: Requisição do frontend local
- **WHEN** o frontend em `http://localhost:5173` faz uma requisição à API
- **THEN** a resposta inclui os cabeçalhos CORS que permitem a origem, os métodos e os cabeçalhos usados


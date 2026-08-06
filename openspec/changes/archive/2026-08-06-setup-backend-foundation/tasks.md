## 1. Estrutura e dependências

- [x] 1.1 Criar a árvore `backend/app/{api,core,models,schemas,services,db}` e `backend/tests/`
- [x] 1.2 Criar `backend/pyproject.toml` com fastapi, uvicorn, sqlalchemy, alembic, pydantic-settings, ortools, openpyxl, pytest
- [x] 1.3 Criar `backend/README.md` com instruções de instalação e execução local
- [x] 1.4 Criar `.gitignore` cobrindo `data/*.db`, `__pycache__/`, ambiente virtual

## 2. Configuração

- [x] 2.1 Implementar `app/core/config.py` com pydantic-settings: `DATABASE_URL` (padrão `sqlite:///data/alocacao.db`), `CENARIOS_DIR` (padrão `data/cenarios/`), limites padrão do solver
- [x] 2.2 Garantir que os diretórios `data/` e `data/cenarios/` sejam criados na inicialização se não existirem

## 3. Camada de banco

- [x] 3.1 Implementar `app/db/session.py` com engine SQLAlchemy, `SessionLocal` e dependência `get_db` para injeção no FastAPI
- [x] 3.2 Implementar `app/db/base.py` com a `Base` declarativa

## 4. Modelo de dados

- [x] 4.1 Modelar `projetos` e `instrutores` (com FK para projeto)
- [x] 4.2 Modelar `instrutor_turno` (turno + carga horária) e `instrutor_dia` (dia da semana 2–6)
- [x] 4.3 Modelar `tipologias` (nome único, carga horária total, horas por encontro) e a relação N:N `instrutor_tipologia`
- [x] 4.4 Modelar `turmas_em_andamento` com FKs para instrutor, tipologia e projeto
- [x] 4.5 Modelar `datas_nao_letivas` com intervalo de datas, tipo e FK opcional para projeto
- [x] 4.6 Modelar `cenarios` (período, caminho do JSON, flag de compartilhamento) e `cenario_projeto`
- [x] 4.7 Modelar `simulacoes`, `turmas_sugeridas`, `turma_sugerida_encontro`, `resultado_kpis` e `snapshot_capacidade`
- [x] 4.8 Definir enums de turno, modalidade, tipo de data não letiva e status de simulação em `app/models/enums.py`
- [x] 4.9 Criar índices para as consultas críticas: turmas sugeridas por simulação, encontros por data, datas não letivas por intervalo

## 5. Migrações

- [x] 5.1 Inicializar Alembic apontando para a `Base` e a `DATABASE_URL` da configuração
- [x] 5.2 Gerar e revisar a migração inicial com todo o esquema
- [x] 5.3 Verificar que a migração aplica em banco vazio e reverte sem erro

## 6. Aplicação

- [x] 6.1 Implementar `app/main.py` criando a aplicação FastAPI com título, versão e docs em `/docs`
- [x] 6.2 Configurar middleware CORS liberando a origem do frontend em desenvolvimento
- [x] 6.3 Implementar `GET /health` retornando status da aplicação e conectividade com o banco
- [x] 6.4 Aplicar migrações pendentes na inicialização, criando o banco se ainda não existir

## 7. Verificação

- [x] 7.1 Escrever teste que sobe a aplicação e valida `GET /health` retornando 200
- [x] 7.2 Escrever teste que cria um instrutor com dois turnos, dois dias e duas tipologias, e confirma a persistência dos relacionamentos
- [x] 7.3 Escrever teste que confirma a rejeição de tipologia com nome duplicado
- [x] 7.4 Rodar a aplicação localmente e conferir o esquema gerado no arquivo SQLite

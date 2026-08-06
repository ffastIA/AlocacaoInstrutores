## Context

Projeto greenfield. O sistema simula quais turmas podem ser abertas a partir da disponibilidade dos instrutores — as turmas são **saída**, não entrada. O usuário final é a equipe de mobilização, sem perfil técnico, e o sistema é aberto (sem autenticação).

O modelo de dados precisa suportar desde já o motor CP-SAT (change `add-class-opening-simulator`), que consome instrutores com granularidade de turno e dia da semana, e produz turmas sugeridas com calendário de encontros.

## Goals / Non-Goals

**Goals:**
- Esqueleto de aplicação FastAPI executável, com healthcheck e docs
- Esquema de dados **completo** do domínio numa única migração inicial
- Configuração por ambiente com padrões que funcionam sem nenhum setup
- Base pronta para as demais changes sem exigir refatoração de esquema

**Non-Goals:**
- Endpoints de negócio (ficam nas changes de ingestão e simulação)
- Lógica do solver
- Autenticação, autorização ou multiusuário
- Deploy, containerização ou CI

## Decisions

### SQLite em vez de Postgres
A escala é pequena (20–60 instrutores), a ferramenta é de apoio à decisão e roda localmente. SQLite elimina a necessidade de subir um serviço de banco, e o arquivo único simplifica backup e compartilhamento de cenários entre membros da equipe. *Alternativa considerada:* Postgres — descartado por adicionar infraestrutura sem benefício na escala atual.

### Esquema completo numa migração inicial
Definir todas as tabelas de uma vez, em vez de deixar cada change criar as suas. As entidades são fortemente relacionadas (instrutor ↔ tipologia ↔ turma ↔ simulação) e fatiá-las geraria migrações redundantes e chaves estrangeiras adicionadas depois. *Trade-off:* a change fica maior, mas evita retrabalho nas seguintes.

### SQLAlchemy + Alembic
ORM maduro com suporte a SQLite, e Alembic dá migrações versionadas desde o início — importante porque a ativação das datas não letivas numa versão futura exigirá evolução de esquema. *Alternativa considerada:* SQL puro com scripts — descartado por perder tipagem e integração com Pydantic.

### Turnos e dias como tabelas, não colunas
A planilha traz turnos e dias como listas (`manha;tarde`, `2;3;4;5`). Modelá-los como tabelas filhas (`instrutor_turno`, `instrutor_dia`) em vez de campos serializados permite ao solver consultar disponibilidade por índice, sem parsing em tempo de execução, e mantém a carga horária pareada ao turno correto.

### JSON apenas para parâmetros de cenário
Dados tabulares consultados por intervalo ficam no SQLite; os pesos do objetivo ficam em JSON porque são configuração versionável, comparável entre cenários e legível/editável fora do sistema. A tabela `cenarios` guarda o caminho do arquivo.

### `snapshot_capacidade` para reprodutibilidade
Uma simulação executada hoje precisa continuar auditável amanhã, mesmo que as turmas em andamento sejam atualizadas. Congelar a capacidade usada por instrutor em cada execução resolve isso sem versionar o banco inteiro.

## Risks / Trade-offs

- **Esquema definido antes das regras estarem implementadas** → mitigado por Alembic: ajustes finos durante as changes seguintes entram como migrações incrementais, não como reescrita
- **SQLite não suporta escrita concorrente** → aceitável: a ferramenta é de uso local e as simulações são disparadas uma por vez; se virar multiusuário, a troca para Postgres é uma mudança de connection string mais ajustes de tipos
- **Ausência de autenticação** → decisão explícita de produto; documentar que o sistema não deve ser exposto publicamente sem uma camada de proteção externa

## Migration Plan

Não aplicável — projeto novo, sem dados legados. A migração inicial cria o esquema do zero.

## Open Questions

- Nomes exatos dos cabeçalhos da planilha real ainda não confirmados — afeta o parser da change `add-data-ingestion`, não o esquema
- Se a ferramenta evoluir para uso simultâneo por vários membros da equipe, avaliar a troca de SQLite por Postgres

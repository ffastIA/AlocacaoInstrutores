## Why

Feriados, recessos e férias deslocam os encontros das turmas no mundo real. Incorporar isso ao cálculo do calendário é complexo — exige decidir se o encontro perdido é pulado ou empurrado, o que torna a duração da turma dependente da data de início e multiplica o pré-cômputo do solver.

A decisão é **separar a coleta do dado do seu uso**: já na v1 o sistema importa e persiste as datas não letivas, mas o gerador de calendário as ignora. Assim a equipe começa a manter esse calendário desde o início, e quando a regra de deslocamento for definida os dados históricos já estarão lá.

## What Changes

- Importação da planilha de **datas não letivas** (`.xlsx`/`.csv`) com intervalos de datas, descrição, tipo e projeto opcional
- Persistência em SQLite na tabela `datas_nao_letivas`
- CRUD para edição pontual do calendário
- Validação de intervalos, com alerta para datas sem efeito prático (sexta-feira e fins de semana, que já não têm aula)
- **Explicitamente sem efeito sobre o cálculo na v1** — a API e a interface deixam isso claro para não gerar expectativa equivocada

## Capabilities

### New Capabilities
- `non-teaching-dates`: importação, persistência e gestão do calendário de datas sem aula

### Modified Capabilities
Nenhuma — o gerador de calendário não é alterado nesta change, por decisão explícita de escopo.

## Impact

- **Novo**: `backend/app/services/importacao/parser_datas_nao_letivas.py`
- **Novo**: rotas `POST /importar/datas-nao-letivas` e CRUD `/datas-nao-letivas`
- **Usa**: a tabela `datas_nao_letivas` definida em `setup-backend-foundation`
- **Não afeta**: o motor de simulação e o gerador de calendário permanecem inalterados
- **Prepara**: a base de dados para a ativação futura do deslocamento de encontros

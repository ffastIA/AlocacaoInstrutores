## Context

Feriados, recessos e férias afetam o calendário real das turmas, mas incorporá-los ao motor CP-SAT tem custo alto: o pré-cômputo do calendário de cada candidata assume hoje que a duração em semanas depende apenas da modalidade e da carga horária. Ao pular datas, a duração passa a depender também da data de início, multiplicando as variantes a pré-computar.

A decisão de produto foi **coletar agora, usar depois**. Esta change entrega a coleta.

## Goals / Non-Goals

**Goals:**
- Importar e persistir o calendário de datas não letivas
- Deixar o dado disponível para consulta por intervalo
- Comunicar sem ambiguidade que o dado ainda não afeta o cálculo

**Non-Goals:**
- Alterar o gerador de encontros ou o motor CP-SAT
- Decidir entre pular e deslocar encontros — é a questão que justifica o adiamento
- Importar feriados de fonte externa automaticamente

## Decisions

### SQLite, não JSON
O dado é tabular, consultado por intervalo (`WHERE data_inicio <= :fim AND data_fim >= :inicio`) e tem integridade referencial com projeto. Esses três atributos apontam para banco relacional. O JSON no projeto está reservado a parâmetros de cenário, que são configuração comparável entre simulações — natureza diferente. *Alternativa considerada:* arquivo JSON de feriados — descartado porque a consulta por interseção de intervalos exigiria carregar e filtrar tudo em memória a cada simulação.

### Intervalo em vez de data individual
Um recesso de fim de ano vira uma linha, não catorze. Reduz o trabalho de preenchimento e mantém a intenção legível na tabela. A expansão em datas individuais, quando for necessária, é derivável em tempo de consulta.

### Sobreposição aceita sem consolidação
Dois registros que se sobrepõem são ambos mantidos. O que importa para o cálculo futuro é a união das datas cobertas, e preservar os registros originais mantém a rastreabilidade de quem cadastrou o quê. Consolidar destruiria informação sem ganho.

### Alerta em vez de rejeição para datas inócuas
Um feriado que cai em sábado é um dado correto, apenas sem efeito. Rejeitá-lo forçaria a equipe a filtrar manualmente a lista oficial de feriados antes de importar. O alerta informa sem criar trabalho.

### Comunicação explícita da limitação
Tanto o retorno da importação quanto a consulta informam que os dados ainda não impactam o cálculo. Sem isso, o usuário cadastraria feriados e concluiria — razoavelmente — que as simulações passaram a considerá-los, gerando confiança indevida no resultado.

## Risks / Trade-offs

- **Usuário assume que os feriados já afetam o resultado** → mitigado pela comunicação explícita na API e por aviso na interface (change `add-frontend-data-screens`)
- **Dados envelhecem antes de serem usados** → baixo impacto: são datas de calendário, que não se invalidam; e a equipe se beneficia de já ter o histórico quando a funcionalidade for ativada

## Migration Plan

Sem migração de dados. A tabela `datas_nao_letivas` já existe desde `setup-backend-foundation`.

**Ativação futura** (fora desta change): o gerador de encontros passará a consultar as datas do período e aplicar a regra escolhida. A decisão pendente é entre pular o encontro (encurtando a carga horária efetiva) ou deslocá-lo (empurrando a sequência e a data de término). A segunda é mais fiel à prática, mas torna `dur_semanas` dependente da data de início.

## Open Questions

- Pular ou deslocar o encontro que cai em data não letiva?
- Se deslocar: a turma pode ultrapassar o fim do período simulado, ou candidatas nessa situação devem ser descartadas?
- Vale importar feriados nacionais de fonte externa automaticamente, ou o cadastro manual é suficiente?

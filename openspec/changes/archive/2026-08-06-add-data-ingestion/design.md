## Context

A equipe de mobilização mantém os dados de instrutores em planilha e não tem perfil técnico. O esquema de dados já existe (`setup-backend-foundation`); falta a camada que traduz planilha em registros de banco.

O ponto não óbvio é a **inversão de dependência do catálogo de tipologias**: tipologia não é um cadastro prévio que o instrutor referencia, mas o contrário — o conjunto de tipologias ofertáveis é a união das habilidades dos instrutores importados. Uma tipologia que ninguém domina simplesmente nunca será ofertada.

## Goals / Non-Goals

**Goals:**
- Importar a planilha real da equipe com o mínimo de reformatação manual
- Nunca perder a planilha inteira por causa de uma linha ruim
- Mensagens de erro que a equipe de mobilização entenda sem apoio técnico
- Derivar tipologias e projetos automaticamente

**Non-Goals:**
- Importação de turmas a abrir — elas são saída da simulação, não entrada
- Datas não letivas (change `add-non-teaching-dates`)
- Interface gráfica de importação (change `add-frontend-data-screens`)
- Deduplicação difusa de nomes (ver Riscos)

## Decisions

### Validação por linha, não por arquivo
Cada linha é validada e persistida isoladamente; as válidas entram mesmo que outras falhem. O retorno traz número da linha e motivo da rejeição. *Alternativa considerada:* transação tudo-ou-nada — descartada porque uma planilha de 60 instrutores com um erro de digitação obrigaria a equipe a reenviar tudo sem saber onde está o problema.

### Cabeçalhos normalizados
A busca de colunas usa o cabeçalho normalizado (minúsculo, sem acento, espaço → underscore), aceitando `Dias Semana`, `dias_semana` e `DIAS SEMANA` como equivalentes. Evita ter que padronizar a planilha antes do primeiro uso.

### Pareamento posicional com falha explícita
`turnos` e `carga_horaria_turno` são pareados por posição. Quando os tamanhos divergem, a linha é rejeitada — nunca se infere um valor faltante. Inferir silenciosamente produziria capacidade errada, e capacidade errada produz simulação errada sem nenhum sinal visível. O parser também aceita o formato explícito `manha:4;tarde:4`, que dispensa o pareamento e é a forma recomendada.

### Tipologia criada como pendente
Ao derivar uma tipologia da planilha de instrutores, ela nasce sem carga horária e é marcada como pendente. A simulação é bloqueada enquanto houver pendências no escopo, com a lista exata do que falta configurar. Isso deixa a lacuna visível cedo, em vez de deixar a simulação rodar com dados incompletos.

### Reimportação atualiza em vez de duplicar
A chave natural é o nome do instrutor. Reimportar substitui turnos, dias e tipologias do instrutor existente. A planilha é a fonte de verdade da disponibilidade, e a equipe vai reimportá-la sempre que a escala mudar.

### Aceitar sobrecarga nas turmas em andamento
Se as turmas em curso já estouram a capacidade declarada de um instrutor, isso é registrado com alerta, não rejeitado. O sistema descreve a realidade; recusar o retrato atual impediria a equipe de simular exatamente o caso em que mais precisa de ajuda.

## Risks / Trade-offs

- **Nomes de instrutor com grafias divergentes entre planilhas** (`Maria Silva` vs `Maria da Silva`) → a v1 usa comparação exata após normalização de espaços e caixa; a turma em andamento que não casar é rejeitada com mensagem clara. Casamento difuso fica fora de escopo por risco de vincular a pessoa errada
- **Cabeçalhos reais ainda não confirmados** → mitigado pela normalização e pelas planilhas-modelo; se divergirem muito, o mapeamento é ajustável em um único ponto do parser
- **Reimportação sobrescreve edições manuais** feitas pela API → documentar que a planilha é a fonte de verdade da disponibilidade

## Open Questions

- Confirmar os cabeçalhos exatos da planilha que a equipe já usa
- Definir se a reimportação deve desativar instrutores ausentes da nova planilha ou apenas ignorá-los

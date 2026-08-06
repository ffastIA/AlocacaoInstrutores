## Context

Estas telas são a porta de entrada dos dados. O usuário é a equipe de mobilização, sem perfil técnico, e o backend já expõe importação, validação e CRUDs.

O risco dominante não é o erro que trava — é o erro que passa. Uma linha rejeitada silenciosamente significa um instrutor ausente da simulação, e o mapa de oportunidades resultante parecerá completo mesmo estando errado.

## Goals / Non-Goals

**Goals:**
- Tornar a importação autoexplicativa, sem consulta a documentação externa
- Comunicar erros de forma acionável: onde está o problema e como corrigi-lo
- Deixar visível o que ainda bloqueia a simulação
- Permitir ajustes pontuais sem exigir reimportação da planilha inteira

**Non-Goals:**
- Edição de planilha dentro do navegador
- Telas de simulação (change seguinte)
- Importação por arrastar e soltar em lote de múltiplos arquivos

## Decisions

### Relatório de importação como resultado principal, não como notificação
O retorno da importação ocupa a tela, com a lista de linhas rejeitadas e seus motivos. Uma notificação temporária desapareceria antes de o usuário conseguir anotar quais linhas corrigir. *Alternativa considerada:* toast de sucesso ou erro — insuficiente para o volume de informação que uma importação parcial produz.

### Erros e alertas visualmente distintos
Erro significa linha não importada; alerta significa linha importada com ressalva. Misturá-los faria o usuário reprocessar dados que já entraram, ou ignorar dados que ficaram de fora.

### Pendências de tipologia com caminho direto
Ao importar instrutores, tipologias novas nascem sem carga horária e bloqueiam a simulação. A tela informa quantas ficaram pendentes e leva direto à configuração — em vez de deixar o usuário descobrir o bloqueio só ao tentar simular.

### Número de encontros exibido antes da confirmação
Ao configurar uma tipologia, a tela mostra o número de encontros resultante da divisão. Torna a regra de divisibilidade evidente pela própria interface, em vez de comunicá-la apenas via mensagem de erro.

### Turmas em andamento ordenadas por data de término
A pergunta que essa tela responde é "quem libera primeiro?". Ordenar por término coloca a informação mais útil no topo, sem exigir ordenação manual.

### Aviso permanente nas datas não letivas
O aviso de que os dados ainda não afetam o cálculo fica fixo na tela, não apenas na confirmação de cadastro. Sem isso, o usuário cadastraria feriados e concluiria — razoavelmente — que as simulações passaram a considerá-los.

### Edição direta além da importação
Cada tela permite ajuste pontual. A planilha continua sendo a fonte de verdade para carga inicial, mas corrigir um turno errado não deve exigir reeditar e reimportar o arquivo inteiro.

## Risks / Trade-offs

- **Edição direta diverge da planilha e é sobrescrita na reimportação** → mitigado por aviso na tela de importação de que a reimportação atualiza os instrutores existentes
- **Lista de erros muito longa em planilha ruim** → apresentar as primeiras ocorrências com opção de expandir, evitando uma parede de texto
- **Usuário ignora o aviso das datas não letivas** → risco residual aceito; o aviso permanente é a mitigação proporcional ao impacto

## Migration Plan

Não aplicável — telas novas.

## Open Questions

- Definir se a listagem de instrutores precisa de exportação para conferência offline
- Avaliar, com uso real, se a lista de erros de importação exige agrupamento por tipo de problema

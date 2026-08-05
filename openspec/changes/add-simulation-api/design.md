## Context

O motor CP-SAT (`add-class-opening-simulator`) resolve o problema mas só roda por script. Esta change o expõe via HTTP para que a equipe de mobilização o use pelo navegador.

Duas características do domínio moldam o design: a simulação pode levar minutos no teto de escala, e o valor da ferramenta está em **comparar cenários** — rodar o mesmo período com prioridades diferentes e ver qual arranjo aproveita melhor a equipe.

## Goals / Non-Goals

**Goals:**
- Executar simulações sem bloquear o cliente
- Persistir resultados de forma que permaneçam auditáveis
- Responder a pergunta central: "a partir de quando posso divulgar turma de cada tipologia?"
- Permitir comparação entre cenários

**Non-Goals:**
- Interface gráfica (changes de frontend)
- Autenticação e controle de acesso
- Fila distribuída ou execução em múltiplas máquinas

## Decisions

### Execução em segundo plano com polling
A simulação roda em background e o cliente consulta o status. *Alternativa considerada:* WebSocket para progresso em tempo real — descartado porque o CP-SAT não expõe progresso granular útil, e polling simples resolve com muito menos complexidade. *Alternativa considerada:* Celery com broker — descartado por exigir infraestrutura adicional numa ferramenta local de uso ocasional.

### Cenário separado de simulação
Um cenário é a **configuração**; uma simulação é uma **execução** daquela configuração. A separação permite reexecutar após atualizar os dados e comparar resultados do mesmo cenário em momentos diferentes. Editar os pesos de um cenário não altera simulações já executadas — elas guardam seu próprio registro do que foi usado.

### Parâmetros em JSON, resultado em SQLite
Os pesos ficam em JSON porque são configuração: legíveis fora do sistema, versionáveis, fáceis de copiar entre cenários. O resultado vai para SQLite porque é dado tabular consultado por filtro e junção. A tabela `cenarios` guarda apenas o caminho do arquivo.

### Falhar em vez de assumir padrões
Se o JSON de parâmetros estiver ausente ou corrompido, a execução falha com erro explícito em vez de usar valores padrão. Uma simulação rodada com pesos diferentes dos que o usuário configurou produziria um resultado plausível e errado — o pior tipo de falha numa ferramenta de apoio à decisão.

### Bloquear execução com dados incompletos
Tipologia sem carga horária configurada impede a simulação, com a lista do que falta. Rodar ignorando essas tipologias produziria um mapa de oportunidades incompleto que o usuário leria como completo.

### Mapa de oportunidades como visão derivada
O mapa não é uma estrutura persistida separadamente: é uma projeção das turmas sugeridas, agrupadas por tipologia e data de início. Evita duplicar dado e garante que mapa e turmas nunca divirjam.

### Snapshot de capacidade por simulação
Cada execução congela a capacidade dos instrutores que utilizou. Sem isso, uma simulação consultada semanas depois seria interpretada contra dados que já mudaram, tornando o resultado inexplicável.

## Risks / Trade-offs

- **SQLite com escrita concorrente durante execução longa** → mitigado por sessão dedicada na tarefa de background e escrita do resultado em transação única ao final
- **Simulação órfã se o processo cair no meio** → o registro fica travado em "executando"; mitigar marcando como erro simulações em execução há mais tempo que o limite configurado
- **Acúmulo de arquivos JSON de cenário** → baixo impacto pelo tamanho; a remoção do cenário apaga também seu arquivo
- **Comparação entre períodos diferentes induz conclusão errada** → mitigado pela sinalização explícita de que os valores absolutos não são comparáveis

## Migration Plan

Não aplicável — funcionalidade nova.

## Open Questions

- Definir o tempo limite após o qual uma simulação travada em "executando" é marcada como erro
- Avaliar se a exportação deve oferecer também formato PDF, além da planilha
- Definir se simulações antigas devem ser expurgadas automaticamente ou mantidas indefinidamente

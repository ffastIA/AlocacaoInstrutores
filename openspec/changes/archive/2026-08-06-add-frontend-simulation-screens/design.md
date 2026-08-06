## Context

Estas telas entregam o valor do sistema. A pergunta que motivou o projeto — "a partir de que data posso divulgar turma de cada tipologia?" — é respondida pelo mapa de oportunidades.

O desafio de apresentação é que o resultado tem três dimensões simultâneas: tipologia, tempo e instrutor. Uma única visualização que tente cobrir as três fica ilegível.

## Goals / Non-Goals

**Goals:**
- Responder à pergunta central em uma tela, sem exigir interpretação
- Tornar o resultado da otimização compreensível para quem não conhece otimização
- Permitir comparar cenários com facilidade, que é o uso recorrente esperado
- Deixar explícito quando o resultado pode não ser o ótimo

**Non-Goals:**
- Edição do resultado da simulação — é sugestão, e a decisão continua com a equipe
- Confirmar turmas sugeridas como turmas reais
- Gráficos elaborados além do necessário para leitura dos indicadores

## Decisions

### Três visões em vez de uma
As três dimensões do resultado são separadas em telas com perguntas distintas:
- **Mapa de oportunidades** — "o que posso abrir e quando?", organizado por tipologia e data
- **Agenda por instrutor** — "quem está ocupado com o quê?", organizado por pessoa e tempo
- **Painel de indicadores** — "esse arranjo é bom?", agregado

Tentar unificar produziria uma matriz densa que não responde bem a nenhuma das três.

### Mapa organizado por tipologia, não por instrutor
A pergunta da equipe é sobre **o que divulgar**, não sobre quem trabalha. A tipologia é a chave primária de organização; o instrutor aparece como quem viabiliza a oportunidade. Inverter isso obrigaria o usuário a percorrer todos os instrutores para descobrir quando cada tipologia fica possível.

### Alternativas de um mesmo instrutor exibidas como escolha
Quando um instrutor multi-tipologia libera capacidade, as tipologias possíveis são apresentadas de forma que fique visível tratar-se de alternativas mutuamente excludentes — não de turmas que serão todas abertas. Sem isso, o usuário superestimaria a capacidade real.

### Pesos exibidos junto ao resultado
O painel mostra os pesos que produziram aquele resultado. É o que torna a comparação entre cenários interpretável: sem os pesos ao lado, dois resultados diferentes parecem inexplicáveis.

### Comunicação explícita da qualidade da solução
Quando o solver esgota o tempo, a interface diz que a busca foi interrompida e que o resultado pode não ser o ótimo. Apresentar como definitivo um resultado interrompido induziria confiança indevida numa ferramenta de apoio à decisão.

### Bloqueios com caminho de correção
Quando a execução é recusada por tipologia pendente, a tela lista as pendências e leva direto à configuração. Uma mensagem de erro sem caminho de saída deixaria o usuário travado.

### Resultado somente leitura
As turmas sugeridas não são editáveis nem confirmáveis. O sistema simula; a decisão e a execução seguem com a equipe. Permitir edição criaria a expectativa de que o sistema gerencia turmas reais, o que não é seu escopo.

### Explicação dos indicadores na própria interface
Cada indicador traz explicação acessível de dentro da tela. "Índice de equilíbrio de tipologias" não é autoexplicativo para quem não trabalha com otimização, e documentação externa não é consultada na prática.

## Risks / Trade-offs

- **Mapa ilegível com muitas tipologias e período longo** → mitigado por filtros de tipologia, instrutor, projeto e intervalo, e por rolagem contida no contêiner. Se o uso real mostrar necessidade, avaliar visualização de linha do tempo dedicada
- **Usuário interpreta alternativas como turmas cumulativas** → mitigado pela apresentação explícita de exclusividade; validar com a equipe no uso real
- **Três telas fragmentam a leitura do resultado** → mitigado por navegação direta entre elas dentro do contexto da mesma simulação
- **Comparação entre períodos diferentes induz conclusão errada** → mitigado pelo alerta explícito

## Migration Plan

Não aplicável — telas novas.

## Open Questions

- Avaliar, com uso real, se o mapa de oportunidades exige visualização de linha do tempo em vez de tabela agrupada
- Definir se a comparação deve permitir mais de três simulações simultâneas ou se isso prejudica a leitura
- Verificar se a equipe sente falta de exportar o mapa em formato de apresentação, além da planilha

## 1. Tela de cenários

- [ ] 1.1 Listar cenários com nome, período, escopo de projetos e pesos, com a ação de executar
- [ ] 1.2 Implementar o formulário de criação e edição
- [ ] 1.3 Implementar o seletor de período impedindo data final anterior à inicial
- [ ] 1.4 Implementar a seleção múltipla de projetos, indicando que vazio abrange todos
- [ ] 1.5 Implementar a alternância de compartilhamento entre projetos, com explicação do seu efeito
- [ ] 1.6 Implementar o ajuste dos quatro pesos, com descrição do que cada critério privilegia
- [ ] 1.7 Impedir confirmação com todos os pesos zerados ou com peso negativo
- [ ] 1.8 Implementar duplicação de cenário
- [ ] 1.9 Implementar estado vazio orientando a criar o primeiro cenário

## 2. Execução e acompanhamento

- [ ] 2.1 Implementar o disparo da simulação a partir do cenário
- [ ] 2.2 Exibir o andamento com tempo decorrido, sem travar a navegação
- [ ] 2.3 Exibir o resultado automaticamente ao concluir, sem atualização manual
- [ ] 2.4 Tratar a recusa por tipologias pendentes, listando-as e oferecendo acesso à configuração
- [ ] 2.5 Tratar a recusa por escopo sem instrutores, sugerindo revisar o cenário ou importar dados
- [ ] 2.6 Tratar falha de execução exibindo a mensagem e mantendo a opção de reexecutar
- [ ] 2.7 Comunicar a qualidade da solução: ótima ou interrompida por tempo
- [ ] 2.8 Tratar resultado sem turmas explicando que não há oportunidade no período

## 3. Mapa de oportunidades

- [ ] 3.1 Implementar a visualização agrupada por tipologia e data de início, em ordem cronológica
- [ ] 3.2 Exibir, por oportunidade, a quantidade de turmas e os instrutores que as sustentam
- [ ] 3.3 Apresentar as alternativas de um mesmo instrutor de forma que fique visível a exclusividade entre elas
- [ ] 3.4 Implementar o detalhe da turma sugerida com modalidade, turno, datas, encontros e carga horária
- [ ] 3.5 Implementar filtros por tipologia, instrutor, projeto e intervalo de datas
- [ ] 3.6 Implementar estado vazio para combinação de filtros sem resultado
- [ ] 3.7 Conter a rolagem horizontal no contêiner, mantendo visíveis a navegação e as tipologias
- [ ] 3.8 Implementar a exportação do resultado em planilha

## 4. Agenda por instrutor

- [ ] 4.1 Implementar a agenda individual com turmas em andamento e sugeridas ao longo do período
- [ ] 4.2 Distinguir visualmente alocação em andamento de sugestão da simulação
- [ ] 4.3 Indicar os turnos e períodos com capacidade ainda livre
- [ ] 4.4 Implementar a visão consolidada com horas alocadas, disponíveis e utilização percentual
- [ ] 4.5 Permitir ordenar por utilização e pela primeira data livre
- [ ] 4.6 Implementar filtro por projeto
- [ ] 4.7 Destacar a primeira data livre de cada instrutor

## 5. Painel de indicadores

- [ ] 5.1 Exibir ociosidade, total de turmas, horas de formação e índices de equilíbrio
- [ ] 5.2 Apresentar a distribuição de turmas por tipologia
- [ ] 5.3 Apresentar a distribuição de utilização entre instrutores
- [ ] 5.4 Exibir os pesos do objetivo que produziram o resultado
- [ ] 5.5 Implementar a explicação acessível de cada indicador
- [ ] 5.6 Exibir a capacidade de reposição disponível às sextas-feiras
- [ ] 5.7 Exibir data da execução, tempo consumido e qualidade da solução

## 6. Comparação e histórico

- [ ] 6.1 Implementar a seleção de simulações para comparar, impedindo incluir as não concluídas
- [ ] 6.2 Exibir os indicadores alinhados lado a lado com destaque das diferenças
- [ ] 6.3 Exibir os parâmetros de cada simulação junto ao seu resultado
- [ ] 6.4 Alertar quando os períodos comparados forem diferentes
- [ ] 6.5 Implementar o histórico ordenado da mais recente para a mais antiga
- [ ] 6.6 Implementar acesso ao mapa e ao painel a partir do histórico
- [ ] 6.7 Implementar filtro do histórico por cenário
- [ ] 6.8 Sinalizar simulações com falha, exibindo a mensagem e sem oferecer acesso a resultados
- [ ] 6.9 Implementar estado vazio do histórico

## 7. Verificação

- [ ] 7.1 Criar cenário pela interface, executar e conferir a exibição automática do resultado
- [ ] 7.2 Conferir o bloqueio por tipologia pendente e o caminho direto para a configuração
- [ ] 7.3 Conferir que o mapa responde a partir de quando cada tipologia pode ser aberta
- [ ] 7.4 Conferir que um instrutor multi-tipologia aparece como alternativa entre tipologias, não como turmas cumulativas
- [ ] 7.5 Conferir a agenda de um instrutor com turma em andamento e turmas sugeridas encadeadas
- [ ] 7.6 Executar dois cenários com pesos diferentes e comparar os resultados
- [ ] 7.7 Conferir o alerta ao comparar simulações de períodos diferentes
- [ ] 7.8 Exportar o resultado e conferir o conteúdo do arquivo
- [ ] 7.9 Conferir os valores exibidos contra a saída do script isolado do motor, para o mesmo conjunto de dados
- [ ] 7.10 Percorrer todas as telas em tema claro e escuro, e navegando apenas pelo teclado

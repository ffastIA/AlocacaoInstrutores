## 1. Tela de cenários

- [x] 1.1 Listar cenários com nome, período, escopo de projetos e pesos, com a ação de executar
- [x] 1.2 Implementar o formulário de criação e edição
- [x] 1.3 Implementar o seletor de período impedindo data final anterior à inicial
- [x] 1.4 Implementar a seleção múltipla de projetos, indicando que vazio abrange todos
- [x] 1.5 Implementar a alternância de compartilhamento entre projetos, com explicação do seu efeito
- [x] 1.6 Implementar o ajuste dos quatro pesos, com descrição do que cada critério privilegia
- [x] 1.7 Impedir confirmação com todos os pesos zerados ou com peso negativo
- [x] 1.8 Implementar duplicação de cenário
- [x] 1.9 Implementar estado vazio orientando a criar o primeiro cenário

## 2. Execução e acompanhamento

- [x] 2.1 Implementar o disparo da simulação a partir do cenário
- [x] 2.2 Exibir o andamento com tempo decorrido, sem travar a navegação
- [x] 2.3 Exibir o resultado automaticamente ao concluir, sem atualização manual
- [x] 2.4 Tratar a recusa por tipologias pendentes, listando-as e oferecendo acesso à configuração
- [x] 2.5 Tratar a recusa por escopo sem instrutores, sugerindo revisar o cenário ou importar dados
- [x] 2.6 Tratar falha de execução exibindo a mensagem e mantendo a opção de reexecutar
- [x] 2.7 Comunicar a qualidade da solução: ótima ou interrompida por tempo
- [x] 2.8 Tratar resultado sem turmas explicando que não há oportunidade no período

## 3. Mapa de oportunidades

- [x] 3.1 Implementar a visualização agrupada por tipologia e data de início, em ordem cronológica
- [x] 3.2 Exibir, por oportunidade, a quantidade de turmas e os instrutores que as sustentam
- [x] 3.3 Apresentar as alternativas de um mesmo instrutor de forma que fique visível a exclusividade entre elas
- [x] 3.4 Implementar o detalhe da turma sugerida com modalidade, turno, datas, encontros e carga horária
- [x] 3.5 Implementar filtros por tipologia, instrutor, projeto e intervalo de datas
- [x] 3.6 Implementar estado vazio para combinação de filtros sem resultado
- [x] 3.7 Conter a rolagem horizontal no contêiner, mantendo visíveis a navegação e as tipologias
- [x] 3.8 Implementar a exportação do resultado em planilha

## 4. Agenda por instrutor

- [x] 4.1 Implementar a agenda individual com turmas em andamento e sugeridas ao longo do período
- [x] 4.2 Distinguir visualmente alocação em andamento de sugestão da simulação
- [x] 4.3 Indicar os turnos e períodos com capacidade ainda livre
- [x] 4.4 Implementar a visão consolidada com horas alocadas, disponíveis e utilização percentual
- [x] 4.5 Permitir ordenar por utilização e pela primeira data livre
- [x] 4.6 Implementar filtro por projeto
- [x] 4.7 Destacar a primeira data livre de cada instrutor

## 5. Painel de indicadores

- [x] 5.1 Exibir ociosidade, total de turmas, horas de formação e índices de equilíbrio
- [x] 5.2 Apresentar a distribuição de turmas por tipologia
- [x] 5.3 Apresentar a distribuição de utilização entre instrutores
- [x] 5.4 Exibir os pesos do objetivo que produziram o resultado
- [x] 5.5 Implementar a explicação acessível de cada indicador
- [x] 5.6 Exibir a capacidade de reposição disponível às sextas-feiras
- [x] 5.7 Exibir data da execução, tempo consumido e qualidade da solução

## 6. Comparação e histórico

- [x] 6.1 Implementar a seleção de simulações para comparar, impedindo incluir as não concluídas
- [x] 6.2 Exibir os indicadores alinhados lado a lado com destaque das diferenças
- [x] 6.3 Exibir os parâmetros de cada simulação junto ao seu resultado
- [x] 6.4 Alertar quando os períodos comparados forem diferentes
- [x] 6.5 Implementar o histórico ordenado da mais recente para a mais antiga
- [x] 6.6 Implementar acesso ao mapa e ao painel a partir do histórico
- [x] 6.7 Implementar filtro do histórico por cenário
- [x] 6.8 Sinalizar simulações com falha, exibindo a mensagem e sem oferecer acesso a resultados
- [x] 6.9 Implementar estado vazio do histórico

## 7. Verificação

- [x] 7.1 Criar cenário pela interface, executar e conferir a exibição automática do resultado
- [x] 7.2 Conferir o bloqueio por tipologia pendente e o caminho direto para a configuração
- [x] 7.3 Conferir que o mapa responde a partir de quando cada tipologia pode ser aberta
- [x] 7.4 Conferir que um instrutor multi-tipologia aparece como alternativa entre tipologias, não como turmas cumulativas
- [x] 7.5 Conferir a agenda de um instrutor com turma em andamento e turmas sugeridas encadeadas
- [x] 7.6 Executar dois cenários com pesos diferentes e comparar os resultados
- [x] 7.7 Conferir o alerta ao comparar simulações de períodos diferentes
- [x] 7.8 Exportar o resultado e conferir o conteúdo do arquivo
- [x] 7.9 Conferir os valores exibidos contra a saída do script isolado do motor, para o mesmo conjunto de dados
- [x] 7.10 Percorrer todas as telas em tema claro e escuro, e navegando apenas pelo teclado

<!-- 7.1-7.3, 7.5, 7.6, 7.8: verificados via curl real (execução, oportunidades,
     agenda, comparação com pesos diferentes, exportação com conteúdo
     conferido) e via teste ao vivo do usuário no navegador (Agenda,
     Indicadores, Mapa) durante a verificação da change refine-turno-slots.

     7.4: confirmado ao vivo no Mapa de Oportunidades (simulação #2) — "Ana
     Costa (alternativa entre tipologias)" aparece como escolha excludente,
     não como turma cumulativa.

     7.7: criado cenário id=2 com período 2027-09-01 a 2027-12-31 (divergente
     do cenário id=1, 2026-08-31 a 2027-04-30), executado como simulação #3,
     e comparado com a simulação #2 em /simulacao/comparacao — o Alert
     "Períodos diferentes" aparece e a linha "Período" é destacada; confirmado
     também via GET /simulacoes/comparar?ids=2,3 (periodos_divergentes: true).

     7.9: rodada uma invocação isolada do motor (gerar_candidatas + resolver +
     calcular_metricas diretamente, fora da API) para o cenário id=1, com os
     mesmos parâmetros persistidos em parametros_json_path. Os KPIs batem
     exatamente com os retornados por GET /simulacoes/2/kpis: status OTIMO,
     total_turmas_sugeridas=135, horas_formacao_total=4966.0,
     pct_ociosidade=12.885154061624648 (igual até a última casa decimal),
     indice_balanceamento_carga=42.85714285714286,
     indice_balanceamento_tipologia=61, slots_reposicao_sexta=105.

     7.10: tema escuro conferido visualmente em Cenários, Situação Atual,
     Agenda por Instrutor, Mapa de Oportunidades (tabela e linha do tempo) —
     contraste e legibilidade OK em todas. Navegação só por teclado testada
     nos marcadores da linha do tempo (a superfície de acessibilidade mais
     nova do app): Tab move o foco com anel visível entre marcadores, Enter
     abre o modal de detalhe, Escape fecha. Tabs/Table/Select/Modal já tinham
     sido auditados no código (role/aria-* corretos) numa revisão completa
     do sistema feita nesta mesma sessão. -->

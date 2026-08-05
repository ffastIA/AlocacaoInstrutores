## 1. Tela de importação

- [ ] 1.1 Montar a tela com uma seção por tipo de planilha: instrutores, tipologias, turmas em andamento e datas não letivas
- [ ] 1.2 Implementar seleção de arquivo com validação de extensão antes do envio
- [ ] 1.3 Exibir progresso durante o envio e desabilitar o botão para impedir envio duplicado
- [ ] 1.4 Implementar o download da planilha-modelo em cada seção
- [ ] 1.5 Descrever, na própria tela, as colunas esperadas e o uso do ponto e vírgula nos campos multivalorados

## 2. Relatório de importação

- [ ] 2.1 Apresentar a contagem de registros importados com sucesso
- [ ] 2.2 Listar as linhas rejeitadas com número da linha e motivo, com opção de expandir quando forem muitas
- [ ] 2.3 Apresentar os alertas em estilo visualmente distinto dos erros
- [ ] 2.4 Tratar a recusa do arquivo inteiro informando a coluna ausente e sugerindo o modelo
- [ ] 2.5 Informar as tipologias que ficaram pendentes e oferecer acesso direto à tela de configuração

## 3. Tela de instrutores

- [ ] 3.1 Listar instrutores com projeto, turnos e cargas horárias, dias da semana e tipologias
- [ ] 3.2 Implementar filtros por projeto e por tipologia
- [ ] 3.3 Implementar edição de turnos, cargas horárias, dias e tipologias
- [ ] 3.4 Exibir erros de validação junto ao campo correspondente, preservando o preenchimento
- [ ] 3.5 Implementar estado vazio orientando a importar a planilha

## 4. Tela de tipologias

- [ ] 4.1 Listar tipologias com carga horária total, horas por encontro e número de instrutores aptos
- [ ] 4.2 Destacar as tipologias pendentes e informar que bloqueiam a simulação
- [ ] 4.3 Implementar a edição de carga horária total e horas por encontro
- [ ] 4.4 Exibir o número de encontros resultante antes da confirmação
- [ ] 4.5 Exibir o erro de divisibilidade explicando que o número de encontros não fecha
- [ ] 4.6 Sinalizar tipologias sem nenhum instrutor apto como nunca ofertáveis, sem tratá-las como bloqueio

## 5. Tela de projetos

- [ ] 5.1 Listar projetos com a quantidade de instrutores vinculados
- [ ] 5.2 Implementar cadastro e edição de projeto

## 6. Tela de situação atual

- [ ] 6.1 Listar as turmas em andamento ordenadas pela data de término prevista
- [ ] 6.2 Implementar cadastro com seleção de instrutor, tipologia, modalidade, turno e datas
- [ ] 6.3 Restringir os turnos oferecidos aos disponíveis do instrutor selecionado
- [ ] 6.4 Validar que a data de término é posterior à de início, exibindo o erro junto ao campo
- [ ] 6.5 Implementar edição e remoção com confirmação de intenção
- [ ] 6.6 Sinalizar instrutores cujas turmas ultrapassam a capacidade declarada
- [ ] 6.7 Implementar estado vazio explicando que a simulação partirá com todos os instrutores livres

## 7. Tela de datas não letivas

- [ ] 7.1 Listar os registros em ordem cronológica com descrição, intervalo, tipo e projeto
- [ ] 7.2 Implementar filtro por período
- [ ] 7.3 Implementar cadastro de dia único e de intervalo, com projeto opcional
- [ ] 7.4 Indicar que o registro sem projeto se aplica a todos
- [ ] 7.5 Implementar edição e remoção com confirmação
- [ ] 7.6 Exibir aviso permanente de que os dados ainda não impactam o cálculo
- [ ] 7.7 Reforçar esse aviso na confirmação de cadastro e de importação
- [ ] 7.8 Sinalizar registros que cobrem apenas sextas-feiras ou fins de semana

## 8. Verificação

- [ ] 8.1 Importar uma planilha válida pela interface e conferir o relatório de sucesso
- [ ] 8.2 Importar uma planilha com linhas inválidas e conferir a listagem das rejeições com número de linha e motivo
- [ ] 8.3 Importar planilha sem coluna obrigatória e conferir a mensagem de recusa
- [ ] 8.4 Conferir que o caminho direto para configuração de tipologias pendentes funciona após importar instrutores
- [ ] 8.5 Configurar uma tipologia e conferir o número de encontros exibido antes da confirmação
- [ ] 8.6 Tentar configurar carga horária não divisível e conferir a mensagem de erro
- [ ] 8.7 Cadastrar turma em andamento com turno incompatível e conferir o bloqueio
- [ ] 8.8 Conferir a ordenação das turmas em andamento pela data de término
- [ ] 8.9 Conferir o aviso permanente na tela de datas não letivas
- [ ] 8.10 Percorrer todas as telas em tema claro e escuro, e navegando apenas pelo teclado

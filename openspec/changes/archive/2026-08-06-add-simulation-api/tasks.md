## 1. Parâmetros de cenário em JSON

- [x] 1.1 Definir o esquema Pydantic dos parâmetros: versão, período, escopo, pesos, normalização, restrições e configuração do solver
- [x] 1.2 Implementar leitura e escrita dos arquivos JSON no diretório configurado
- [x] 1.3 Falhar com erro explícito quando o arquivo estiver ausente ou não puder ser interpretado
- [x] 1.4 Gerar nome de arquivo único por cenário

## 2. CRUD de cenários

- [x] 2.1 Implementar criação de cenário gravando metadados em SQLite e parâmetros em JSON
- [x] 2.2 Implementar consulta e listagem de cenários com seus parâmetros
- [x] 2.3 Implementar edição, atualizando o arquivo JSON sem afetar simulações já executadas
- [x] 2.4 Implementar remoção, apagando também o arquivo de parâmetros
- [x] 2.5 Implementar duplicação de cenário com novo arquivo de parâmetros
- [x] 2.6 Validar período, pesos não negativos, ao menos um peso positivo e escopo de projetos

## 3. Execução assíncrona

- [x] 3.1 Implementar `POST /simulacoes/executar` criando o registro com status pendente e retornando o identificador
- [x] 3.2 Implementar a tarefa de background que carrega os dados, monta o modelo e executa o solver
- [x] 3.3 Usar sessão de banco dedicada na tarefa de background
- [x] 3.4 Atualizar status ao longo do ciclo: pendente, executando, concluída ou erro
- [x] 3.5 Registrar tempo de execução, status do solver e valor do objetivo ao concluir
- [x] 3.6 Capturar exceções, registrando status de erro com a mensagem
- [x] 3.7 Bloquear a execução quando houver tipologia pendente de configuração no escopo
- [x] 3.8 Bloquear a execução quando o escopo não contiver nenhum instrutor

## 4. Persistência do resultado

- [x] 4.1 Persistir as turmas sugeridas com todos os seus atributos
- [x] 4.2 Persistir o calendário de encontros de cada turma sugerida
- [x] 4.3 Persistir os KPIs calculados pelo motor
- [x] 4.4 Persistir o snapshot de capacidade por instrutor
- [x] 4.5 Gravar o resultado em transação única ao final da execução
- [x] 4.6 Tratar resultado vazio como conclusão normal, não como erro

## 5. Consultas de resultado

- [x] 5.1 Implementar `GET /simulacoes/{id}` com status e metadados de execução
- [x] 5.2 Implementar `GET /simulacoes/{id}/turmas-sugeridas` com os calendários
- [x] 5.3 Implementar `GET /simulacoes/{id}/kpis`
- [x] 5.4 Implementar `GET /simulacoes/{id}/oportunidades` agrupando por tipologia e data de início, em ordem cronológica
- [x] 5.5 Implementar `GET /simulacoes/{id}/agenda/{instrutor_id}` combinando turmas em andamento e sugeridas, distinguindo a origem de cada uma
- [x] 5.6 Implementar `GET /simulacoes` com paginação, ordenação por data e filtro por cenário
- [x] 5.7 Retornar HTTP 404 para identificadores inexistentes

## 6. Comparação

- [x] 6.1 Implementar `GET /simulacoes/comparar` recebendo múltiplos identificadores
- [x] 6.2 Alinhar os KPIs das simulações para leitura lado a lado e calcular as diferenças
- [x] 6.3 Incluir os parâmetros de cada cenário no retorno
- [x] 6.4 Sinalizar quando os períodos comparados forem diferentes
- [x] 6.5 Recusar a comparação quando alguma simulação não estiver concluída ou não existir

## 7. Exportação

- [x] 7.1 Implementar geração de planilha com as turmas sugeridas
- [x] 7.2 Incluir aba ou seção com os KPIs e os parâmetros do cenário
- [x] 7.3 Nomear o arquivo com identificação do cenário e data da execução
- [x] 7.4 Recusar exportação de simulação não concluída
- [x] 7.5 Implementar `GET /simulacoes/{id}/exportar`

## 8. Verificação

- [x] 8.1 Testar criação de cenário e a geração correta do arquivo JSON
- [x] 8.2 Testar rejeição por período invertido, pesos negativos e todos os pesos nulos
- [x] 8.3 Testar que editar os pesos de um cenário não altera simulações já executadas
- [x] 8.4 Testar disparo assíncrono retornando identificador antes da conclusão
- [x] 8.5 Testar transição de status até a conclusão e a persistência do resultado
- [x] 8.6 Testar bloqueio por tipologia pendente de configuração
- [x] 8.7 Testar que o mapa de oportunidades agrupa por tipologia e data em ordem cronológica
- [x] 8.8 Testar que uma simulação antiga mantém seu resultado após as turmas em andamento mudarem
- [x] 8.9 Testar comparação entre dois cenários e a recusa quando um deles não concluiu
- [x] 8.10 Testar exportação e a recusa para simulação em execução
- [x] 8.11 Exercitar o fluxo completo via Swagger: importar dados, criar cenário, simular, consultar oportunidades e exportar

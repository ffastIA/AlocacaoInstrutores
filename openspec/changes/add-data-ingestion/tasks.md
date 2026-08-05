## 1. Infraestrutura de parsing

- [ ] 1.1 Implementar `services/importacao/leitor_planilha.py` lendo `.xlsx` e `.csv` para uma lista de dicionários
- [ ] 1.2 Implementar normalização de cabeçalhos (minúsculo, sem acento, espaço → underscore) e localização de colunas por nome normalizado
- [ ] 1.3 Implementar utilitário de parse de lista separada por `;`, com remoção de espaços nas extremidades
- [ ] 1.4 Implementar `ResultadoImportacao` com contagem de sucessos, lista de erros por linha e lista de alertas

## 2. Parser de instrutores

- [ ] 2.1 Implementar `parser_instrutores.py` mapeando as colunas e validando as obrigatórias
- [ ] 2.2 Implementar o pareamento posicional turnos ↔ carga horária, rejeitando listas de tamanhos diferentes
- [ ] 2.3 Aceitar o formato alternativo explícito `manha:4;tarde:4` sem a coluna de carga horária
- [ ] 2.4 Validar turnos contra os valores permitidos e dias da semana contra a faixa de 2 a 6
- [ ] 2.5 Rejeitar linha sem nenhuma tipologia
- [ ] 2.6 Persistir instrutor, turnos, dias e vínculos de tipologia
- [ ] 2.7 Implementar reimportação: atualizar instrutor existente pelo nome em vez de duplicar

## 3. Derivação de catálogo

- [ ] 3.1 Criar tipologias inéditas encontradas na planilha, marcadas como pendentes de configuração
- [ ] 3.2 Criar projetos inéditos encontrados na planilha
- [ ] 3.3 Reutilizar tipologias e projetos já existentes sem sobrescrever sua configuração

## 4. Parser de tipologias

- [ ] 4.1 Implementar `parser_tipologias.py` lendo tipologia, carga horária total, horas por encontro e descrição
- [ ] 4.2 Validar que a carga horária total é múltiplo exato das horas por encontro
- [ ] 4.3 Validar que a carga horária total está na faixa de 24 a 60 horas
- [ ] 4.4 Atualizar a tipologia existente e remover a marcação de pendente
- [ ] 4.5 Emitir alerta para tipologia que nenhum instrutor domina

## 5. Parser de turmas em andamento

- [ ] 5.1 Implementar `parser_turmas_andamento.py` com resolução de instrutor e tipologia por nome
- [ ] 5.2 Validar modalidade contra os valores permitidos e turno contra a disponibilidade do instrutor
- [ ] 5.3 Validar que a data de término é posterior à data de início
- [ ] 5.4 Emitir alerta — sem rejeitar — quando as turmas em andamento estouram a capacidade do instrutor
- [ ] 5.5 Tratar planilha vazia como situação válida

## 6. Planilhas-modelo

- [ ] 6.1 Implementar gerador de `.xlsx` em branco com cabeçalhos corretos por tipo
- [ ] 6.2 Incluir linha de exemplo demonstrando o formato dos campos multivalorados
- [ ] 6.3 Retornar erro com a lista de tipos disponíveis quando o tipo solicitado não existe

## 7. Endpoints

- [ ] 7.1 Implementar `POST /importar/instrutores`, `/importar/tipologias` e `/importar/turmas-em-andamento` recebendo upload e retornando o relatório de validação
- [ ] 7.2 Implementar `GET /importar/modelos/{tipo}` para download das planilhas-modelo
- [ ] 7.3 Implementar CRUD de `/projetos`, `/tipologias`, `/instrutores` e `/turmas-em-andamento`
- [ ] 7.4 Implementar `GET /tipologias/pendentes` listando as tipologias sem carga horária configurada

## 8. Verificação

- [ ] 8.1 Testar importação bem-sucedida com planilha de exemplo contendo múltiplos turnos, dias e tipologias
- [ ] 8.2 Testar rejeição por desalinhamento entre turnos e cargas horárias
- [ ] 8.3 Testar que uma planilha com linhas válidas e inválidas importa as válidas e reporta as demais
- [ ] 8.4 Testar reconhecimento de cabeçalhos com acento, maiúsculas e ordem trocada
- [ ] 8.5 Testar derivação automática de tipologia e projeto inéditos
- [ ] 8.6 Testar rejeição de tipologia com carga horária não divisível pelas horas por encontro
- [ ] 8.7 Testar rejeição de turma em andamento com turno incompatível com o instrutor
- [ ] 8.8 Testar reimportação atualizando um instrutor existente sem duplicá-lo
- [ ] 8.9 Exercitar o fluxo completo via Swagger: baixar modelo, preencher, importar e conferir os dados

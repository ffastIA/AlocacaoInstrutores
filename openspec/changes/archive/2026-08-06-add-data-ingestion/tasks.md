## 1. Infraestrutura de parsing

- [x] 1.1 Implementar `services/importacao/leitor_planilha.py` lendo `.xlsx` e `.csv` para uma lista de dicionários
- [x] 1.2 Implementar normalização de cabeçalhos (minúsculo, sem acento, espaço → underscore) e localização de colunas por nome normalizado
- [x] 1.3 Implementar utilitário de parse de lista separada por `;`, com remoção de espaços nas extremidades
- [x] 1.4 Implementar `ResultadoImportacao` com contagem de sucessos, lista de erros por linha e lista de alertas

## 2. Parser de instrutores

- [x] 2.1 Implementar `parser_instrutores.py` mapeando as colunas e validando as obrigatórias
- [x] 2.2 Implementar o pareamento posicional turnos ↔ carga horária, rejeitando listas de tamanhos diferentes
- [x] 2.3 Aceitar o formato alternativo explícito `manha:4;tarde:4` sem a coluna de carga horária
- [x] 2.4 Validar turnos contra os valores permitidos e dias da semana contra a faixa de 2 a 6
- [x] 2.5 Rejeitar linha sem nenhuma tipologia
- [x] 2.6 Persistir instrutor, turnos, dias e vínculos de tipologia
- [x] 2.7 Implementar reimportação: atualizar instrutor existente pelo nome em vez de duplicar

## 3. Derivação de catálogo

- [x] 3.1 Criar tipologias inéditas encontradas na planilha, marcadas como pendentes de configuração
- [x] 3.2 Criar projetos inéditos encontrados na planilha
- [x] 3.3 Reutilizar tipologias e projetos já existentes sem sobrescrever sua configuração

## 4. Parser de tipologias

- [x] 4.1 Implementar `parser_tipologias.py` lendo tipologia, carga horária total, horas por encontro e descrição
- [x] 4.2 Validar que a carga horária total é múltiplo exato das horas por encontro
- [x] 4.3 Validar que a carga horária total está na faixa de 24 a 60 horas
- [x] 4.4 Atualizar a tipologia existente e remover a marcação de pendente
- [x] 4.5 Emitir alerta para tipologia que nenhum instrutor domina

## 5. Parser de turmas em andamento

- [x] 5.1 Implementar `parser_turmas_andamento.py` com resolução de instrutor e tipologia por nome
- [x] 5.2 Validar modalidade contra os valores permitidos e turno contra a disponibilidade do instrutor
- [x] 5.3 Validar que a data de término é posterior à data de início
- [x] 5.4 Emitir alerta — sem rejeitar — quando as turmas em andamento estouram a capacidade do instrutor
- [x] 5.5 Tratar planilha vazia como situação válida

## 6. Planilhas-modelo

- [x] 6.1 Implementar gerador de `.xlsx` em branco com cabeçalhos corretos por tipo
- [x] 6.2 Incluir linha de exemplo demonstrando o formato dos campos multivalorados
- [x] 6.3 Retornar erro com a lista de tipos disponíveis quando o tipo solicitado não existe

## 7. Endpoints

- [x] 7.1 Implementar `POST /importar/instrutores`, `/importar/tipologias` e `/importar/turmas-em-andamento` recebendo upload e retornando o relatório de validação
- [x] 7.2 Implementar `GET /importar/modelos/{tipo}` para download das planilhas-modelo
- [x] 7.3 Implementar CRUD de `/projetos`, `/tipologias`, `/instrutores` e `/turmas-em-andamento`
- [x] 7.4 Implementar `GET /tipologias/pendentes` listando as tipologias sem carga horária configurada

## 8. Verificação

- [x] 8.1 Testar importação bem-sucedida com planilha de exemplo contendo múltiplos turnos, dias e tipologias
- [x] 8.2 Testar rejeição por desalinhamento entre turnos e cargas horárias
- [x] 8.3 Testar que uma planilha com linhas válidas e inválidas importa as válidas e reporta as demais
- [x] 8.4 Testar reconhecimento de cabeçalhos com acento, maiúsculas e ordem trocada
- [x] 8.5 Testar derivação automática de tipologia e projeto inéditos
- [x] 8.6 Testar rejeição de tipologia com carga horária não divisível pelas horas por encontro
- [x] 8.7 Testar rejeição de turma em andamento com turno incompatível com o instrutor
- [x] 8.8 Testar reimportação atualizando um instrutor existente sem duplicá-lo
- [x] 8.9 Exercitar o fluxo completo via Swagger: baixar modelo, preencher, importar e conferir os dados

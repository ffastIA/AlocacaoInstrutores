# api-client Specification

## Purpose
TBD - created by archiving change setup-frontend-foundation. Update Purpose after archive.
## Requirements
### Requirement: Cliente HTTP tipado
O sistema SHALL prover uma camada de acesso ao backend com tipos correspondentes aos contratos da API.

#### Scenario: Chamada tipada
- **WHEN** uma tela consome um endpoint pelo cliente
- **THEN** o retorno é tipado, e divergências de contrato são apontadas em tempo de compilação

#### Scenario: URL base configurável
- **WHEN** a aplicação é construída para outro ambiente
- **THEN** a URL base da API é definida por variável de ambiente, sem alteração de código

### Requirement: Tratamento centralizado de erros
O sistema SHALL tratar falhas de requisição em um único ponto, apresentando mensagens compreensíveis ao usuário.

#### Scenario: Erro de validação retornado pela API
- **WHEN** o backend responde com erro de validação
- **THEN** a interface exibe a mensagem retornada, sem expor detalhes técnicos da resposta

#### Scenario: Backend indisponível
- **WHEN** a requisição falha por indisponibilidade do servidor
- **THEN** a interface informa que não foi possível conectar ao servidor e oferece a opção de tentar novamente

#### Scenario: Recurso não encontrado
- **WHEN** o backend responde que o recurso não existe
- **THEN** a interface informa a ausência do recurso, sem apresentar tela de erro genérica

### Requirement: Upload de planilhas
O sistema SHALL suportar envio de arquivos ao backend com acompanhamento do progresso.

#### Scenario: Envio de arquivo
- **WHEN** o usuário envia uma planilha
- **THEN** o cliente transmite o arquivo e informa o progresso do envio

#### Scenario: Relatório de importação
- **WHEN** o backend responde ao upload com o relatório de validação
- **THEN** o cliente entrega à tela a contagem de sucessos, a lista de erros por linha e os alertas

### Requirement: Acompanhamento de operações assíncronas
O sistema SHALL acompanhar o andamento de simulações em execução por consulta periódica.

#### Scenario: Consulta durante o processamento
- **WHEN** uma simulação está em execução
- **THEN** o cliente consulta o status periodicamente até a conclusão ou o erro

#### Scenario: Encerramento da consulta
- **WHEN** a simulação conclui ou falha
- **THEN** o cliente interrompe as consultas e entrega o resultado final à tela


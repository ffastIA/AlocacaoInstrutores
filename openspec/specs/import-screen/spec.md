# import-screen Specification

## Purpose
TBD - created by archiving change add-frontend-data-screens. Update Purpose after archive.
## Requirements
### Requirement: Upload de planilhas
O sistema SHALL permitir enviar as planilhas de instrutores, tipologias, turmas em andamento e datas não letivas pela interface.

#### Scenario: Seleção e envio
- **WHEN** o usuário seleciona um arquivo e confirma o envio
- **THEN** a interface envia o arquivo, exibe o progresso e apresenta o resultado ao final

#### Scenario: Formato não suportado
- **WHEN** o usuário seleciona um arquivo que não é planilha
- **THEN** a interface recusa o envio informando os formatos aceitos

#### Scenario: Envio em andamento
- **WHEN** um envio está em curso
- **THEN** o botão de envio fica desabilitado até a conclusão, impedindo envio duplicado

### Requirement: Download de planilhas-modelo
O sistema SHALL oferecer o download do modelo correspondente a cada tipo de importação.

#### Scenario: Modelo disponível junto ao upload
- **WHEN** o usuário acessa a tela de importação
- **THEN** cada tipo de planilha apresenta a opção de baixar o respectivo modelo

### Requirement: Relatório de importação
O sistema SHALL apresentar o resultado da importação de forma que o usuário identifique e corrija os problemas sem apoio técnico.

#### Scenario: Importação sem erros
- **WHEN** todas as linhas são importadas com sucesso
- **THEN** a interface confirma a conclusão informando a quantidade de registros importados

#### Scenario: Importação parcial
- **WHEN** parte das linhas é rejeitada
- **THEN** a interface informa quantas foram importadas e apresenta a lista das rejeitadas, com o número da linha e o motivo de cada rejeição

#### Scenario: Arquivo inteiro recusado
- **WHEN** o arquivo é recusado por ausência de coluna obrigatória
- **THEN** a interface informa qual coluna está faltando e sugere baixar o modelo

#### Scenario: Alertas
- **WHEN** a importação gera alertas sem rejeitar linhas
- **THEN** a interface apresenta os alertas de forma distinta dos erros, deixando claro que os dados foram importados

### Requirement: Orientação sobre o formato esperado
O sistema SHALL apresentar, na própria tela, o formato esperado de cada planilha.

#### Scenario: Consulta do formato
- **WHEN** o usuário acessa a tela de importação
- **THEN** a interface descreve as colunas de cada planilha e exemplifica o uso do ponto e vírgula nos campos multivalorados

### Requirement: Indicação de próximos passos
O sistema SHALL orientar o usuário sobre o que fazer após cada importação.

#### Scenario: Tipologias pendentes após importar instrutores
- **WHEN** a importação de instrutores deriva tipologias sem carga horária configurada
- **THEN** a interface informa quantas tipologias ficaram pendentes e oferece acesso direto à tela de configuração


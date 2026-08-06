# typology-catalog Specification

## Purpose
TBD - created by archiving change add-data-ingestion. Update Purpose after archive.
## Requirements
### Requirement: Configuração de carga horária das tipologias
O sistema SHALL permitir configurar, por tipologia, a carga horária total e as horas por encontro — via importação de planilha ou edição direta.

#### Scenario: Configuração por planilha
- **WHEN** a planilha de tipologias é importada com `Robótica; 40; 4`
- **THEN** o sistema atualiza a tipologia Robótica com 40 horas totais e 4 horas por encontro, deixando-a apta a gerar turmas

#### Scenario: Edição direta
- **WHEN** o usuário altera as horas por encontro de uma tipologia pela API
- **THEN** o sistema persiste o novo valor

### Requirement: Consistência entre carga total e horas por encontro
O sistema SHALL exigir que a carga horária total seja múltiplo exato das horas por encontro.

#### Scenario: Carga horária divisível
- **WHEN** uma tipologia é configurada com 40 horas totais e 4 horas por encontro
- **THEN** o sistema aceita a configuração, da qual derivam 10 encontros

#### Scenario: Carga horária não divisível
- **WHEN** uma tipologia é configurada com 50 horas totais e 4 horas por encontro
- **THEN** o sistema rejeita a configuração, pois o número de encontros não fecha em valor inteiro

#### Scenario: Carga horária fora da faixa permitida
- **WHEN** uma tipologia é configurada com carga horária total fora da faixa de 24 a 60 horas
- **THEN** o sistema rejeita a configuração informando a faixa válida

### Requirement: Sinalização de tipologias pendentes
O sistema SHALL identificar as tipologias derivadas da planilha de instrutores que ainda não têm carga horária configurada.

#### Scenario: Consulta de pendências
- **WHEN** o usuário consulta o catálogo após importar instrutores mas antes de configurar as cargas horárias
- **THEN** o sistema lista as tipologias marcadas como pendentes de configuração

#### Scenario: Bloqueio da simulação
- **WHEN** uma simulação é solicitada e existe tipologia pendente no escopo
- **THEN** o sistema bloqueia a execução e informa quais tipologias precisam ser configuradas

### Requirement: Alerta para tipologia sem instrutor
O sistema SHALL alertar — sem rejeitar — quando a planilha de tipologias trouxer uma tipologia que nenhum instrutor domina.

#### Scenario: Tipologia órfã
- **WHEN** a planilha de tipologias traz uma tipologia ausente das habilidades de todos os instrutores
- **THEN** o sistema importa o registro e emite alerta de que essa tipologia nunca será ofertada


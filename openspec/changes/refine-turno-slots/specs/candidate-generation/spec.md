## MODIFIED Requirements

### Requirement: Poda por elegibilidade
O sistema SHALL descartar na enumeração — sem criar variável de decisão — toda combinação inviável.

#### Scenario: Tipologia não dominada
- **WHEN** uma tipologia não consta nas habilidades do instrutor
- **THEN** nenhuma candidata é gerada para aquele par instrutor–tipologia

#### Scenario: Slot de turno indisponível
- **WHEN** um slot de turno não consta na disponibilidade do instrutor
- **THEN** nenhuma candidata é gerada para aquele par instrutor–slot

#### Scenario: Dias da semana incompatíveis com a modalidade
- **WHEN** um instrutor está disponível apenas às segundas e quartas
- **THEN** o sistema gera candidatas na modalidade `regular_seg_qua`, mas nenhuma nas modalidades `regular_ter_qui` e `intensiva_seg_qui`

#### Scenario: Semana anterior à liberação do instrutor
- **WHEN** o instrutor não tem nenhum slot livre antes de determinada data
- **THEN** nenhuma candidata é gerada com semana de início anterior a essa data

# class-calendar Specification

## Purpose
TBD - created by archiving change add-class-opening-simulator. Update Purpose after archive.
## Requirements
### Requirement: Geração determinística do calendário de encontros
O sistema SHALL gerar, a partir de tipologia, modalidade e semana de início, a sequência completa de encontros de uma turma — cada um com data, turno e carga horária.

#### Scenario: Turma regular em dias intercalados
- **WHEN** uma tipologia de 40 horas com 4 horas por encontro é gerada na modalidade `regular_seg_qua`
- **THEN** o sistema produz 10 encontros distribuídos em segundas e quartas, ao longo de 5 semanas

#### Scenario: Turma intensiva
- **WHEN** a mesma tipologia de 40 horas é gerada na modalidade `intensiva_seg_qui`
- **THEN** o sistema produz 10 encontros distribuídos de segunda a quinta, concluindo em menos semanas que a modalidade regular

#### Scenario: Determinismo
- **WHEN** o calendário é gerado duas vezes com os mesmos parâmetros
- **THEN** o sistema produz exatamente a mesma sequência de datas

### Requirement: Ausência de encontros às sextas-feiras
O sistema SHALL garantir que nenhum encontro de turma regular seja agendado em uma sexta-feira, reservada a atividades extraclasse e reposição.

#### Scenario: Qualquer modalidade
- **WHEN** um calendário é gerado em qualquer modalidade e qualquer semana de início
- **THEN** nenhuma data da sequência cai em uma sexta-feira

### Requirement: Derivação do número de encontros
O sistema SHALL derivar o número de encontros dividindo a carga horária total da tipologia pelas suas horas por encontro.

#### Scenario: Divisão exata
- **WHEN** uma tipologia de 24 horas com 2 horas por encontro é gerada
- **THEN** o sistema produz exatamente 12 encontros

#### Scenario: Carga horária total preservada
- **WHEN** um calendário é gerado
- **THEN** a soma das horas de todos os encontros é igual à carga horária total da tipologia

### Requirement: Cálculo da data de término
O sistema SHALL calcular a data de término da turma como a data do seu último encontro.

#### Scenario: Término coerente com a modalidade
- **WHEN** duas turmas da mesma tipologia iniciam na mesma semana, uma regular e outra intensiva
- **THEN** a data de término da intensiva é anterior à da regular


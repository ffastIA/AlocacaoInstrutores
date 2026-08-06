# non-teaching-dates Specification

## Purpose
TBD - created by archiving change add-non-teaching-dates. Update Purpose after archive.
## Requirements
### Requirement: Importação do calendário de datas não letivas
O sistema SHALL aceitar upload de planilha contendo feriados, recessos e períodos de férias, persistindo os registros válidos.

#### Scenario: Importação de dia único
- **WHEN** uma linha traz apenas `data_inicio` preenchida
- **THEN** o sistema persiste um intervalo de um único dia, com data de término igual à de início

#### Scenario: Importação de intervalo
- **WHEN** uma linha traz `data_inicio = 24/12/2026` e `data_fim = 06/01/2027`
- **THEN** o sistema persiste o intervalo completo como um único registro

#### Scenario: Tipo omitido
- **WHEN** uma linha não informa o campo `tipo`
- **THEN** o sistema assume o tipo `feriado`

### Requirement: Escopo por projeto
O sistema SHALL permitir que uma data não letiva se aplique a um projeto específico ou a todos os projetos.

#### Scenario: Data global
- **WHEN** uma linha não informa projeto
- **THEN** o sistema persiste o registro sem vínculo a projeto, indicando que vale para todos

#### Scenario: Data restrita a um projeto
- **WHEN** uma linha informa um projeto existente
- **THEN** o sistema vincula o registro àquele projeto

#### Scenario: Projeto inexistente
- **WHEN** uma linha informa um projeto que não está cadastrado
- **THEN** o sistema rejeita a linha informando o projeto não encontrado

### Requirement: Validação de intervalos
O sistema SHALL validar a coerência das datas informadas.

#### Scenario: Data de término anterior à de início
- **WHEN** uma linha traz `data_fim` anterior a `data_inicio`
- **THEN** o sistema rejeita a linha informando a inconsistência

#### Scenario: Formato de data inválido
- **WHEN** uma linha traz uma data que não segue o formato `DD/MM/AAAA`
- **THEN** o sistema rejeita a linha informando o formato esperado

#### Scenario: Intervalos sobrepostos
- **WHEN** duas linhas descrevem intervalos que se sobrepõem
- **THEN** o sistema aceita ambos os registros, pois o que importa é a união das datas cobertas

### Requirement: Alerta para datas sem efeito prático
O sistema SHALL sinalizar datas não letivas que caem em dias que já não têm aula.

#### Scenario: Feriado em fim de semana
- **WHEN** uma data não letiva cai em um sábado ou domingo
- **THEN** o sistema importa o registro e emite alerta de que não terá efeito prático

#### Scenario: Feriado em sexta-feira
- **WHEN** uma data não letiva cai em uma sexta-feira
- **THEN** o sistema importa o registro e emite alerta, já que sextas não recebem turma regular

### Requirement: Gestão do calendário
O sistema SHALL permitir consultar, criar, editar e remover datas não letivas diretamente, sem depender de reimportação.

#### Scenario: Consulta por período
- **WHEN** o usuário consulta as datas não letivas de um intervalo
- **THEN** o sistema retorna todos os registros que interseccionam aquele intervalo

#### Scenario: Remoção de registro
- **WHEN** o usuário remove uma data não letiva
- **THEN** o sistema exclui o registro sem afetar simulações já executadas

### Requirement: Ausência de efeito sobre o cálculo na versão atual
O sistema SHALL persistir as datas não letivas sem alterar a geração de calendários de turma, e SHALL comunicar essa limitação de forma explícita.

#### Scenario: Simulação com datas não letivas cadastradas
- **WHEN** uma simulação é executada com feriados cadastrados dentro do período simulado
- **THEN** os calendários das turmas sugeridas são gerados como se não houvesse feriados, e o resultado permanece idêntico ao de uma base sem esses registros

#### Scenario: Comunicação da limitação
- **WHEN** o usuário importa ou consulta datas não letivas
- **THEN** a resposta informa explicitamente que os dados ainda não impactam o cálculo das simulações


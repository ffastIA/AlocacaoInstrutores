## ADDED Requirements

### Requirement: Tokens visuais centralizados
O sistema SHALL definir cores, tipografia, espaçamentos, raios de borda e sombras como tokens reutilizáveis, consumidos por todos os componentes.

#### Scenario: Alteração centralizada
- **WHEN** a cor primária é alterada no arquivo de tokens
- **THEN** todos os componentes que a utilizam refletem a mudança, sem edição individual

#### Scenario: Ausência de valores literais
- **WHEN** um componente base define cor, espaçamento ou tamanho de fonte
- **THEN** ele referencia um token, nunca um valor literal

### Requirement: Tema claro e escuro
O sistema SHALL suportar tema claro e escuro, respeitando a preferência do sistema operacional e permitindo alternância manual.

#### Scenario: Preferência do sistema
- **WHEN** o usuário abre a aplicação com o sistema operacional em modo escuro
- **THEN** a interface é exibida em tema escuro

#### Scenario: Alternância manual
- **WHEN** o usuário alterna o tema pelo controle da interface
- **THEN** a aplicação aplica o tema escolhido imediatamente e o mantém entre visitas

#### Scenario: Legibilidade em ambos os temas
- **WHEN** qualquer tela é exibida em tema claro ou escuro
- **THEN** o contraste entre texto e fundo atende ao nível AA das diretrizes de acessibilidade

### Requirement: Componentes base
O sistema SHALL prover uma biblioteca de componentes reutilizáveis cobrindo as necessidades das telas previstas.

#### Scenario: Conjunto disponível
- **WHEN** uma tela é construída
- **THEN** estão disponíveis botão, campo de texto, campo numérico, seleção, seletor de data, tabela, cartão, modal, aviso, indicador de carregamento e estado vazio

#### Scenario: Estados dos componentes interativos
- **WHEN** um componente interativo é usado
- **THEN** ele apresenta os estados normal, foco, desabilitado e — quando aplicável — carregando e erro

#### Scenario: Navegação por teclado
- **WHEN** o usuário navega pela interface usando apenas o teclado
- **THEN** todos os componentes interativos são alcançáveis e apresentam indicador de foco visível

### Requirement: Apresentação de tabelas extensas
O sistema SHALL exibir tabelas largas sem provocar rolagem horizontal da página inteira.

#### Scenario: Tabela mais larga que a área de conteúdo
- **WHEN** uma tabela excede a largura disponível
- **THEN** a rolagem horizontal ocorre dentro do próprio contêiner da tabela, e o corpo da página permanece sem rolagem lateral

### Requirement: Comunicação de estados da interface
O sistema SHALL apresentar de forma explícita os estados de carregamento, erro e ausência de dados.

#### Scenario: Carregamento
- **WHEN** dados estão sendo buscados
- **THEN** a interface exibe indicador de carregamento no lugar do conteúdo

#### Scenario: Ausência de dados
- **WHEN** uma consulta retorna vazia
- **THEN** a interface exibe um estado vazio explicando o que falta e qual a próxima ação possível

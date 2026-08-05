## Why

A API resolve o problema, mas a equipe de mobilização não vai usar Swagger. Precisa de uma interface que carregue planilhas, ajuste prioridades e leia o mapa de oportunidades sem apoio técnico.

Antes das telas, é preciso estabelecer a base: aplicação React, cliente HTTP, roteamento e — principalmente — o **estilo de página**. Definir paleta, tipografia e componentes base uma única vez evita que cada tela invente sua própria aparência e produza uma interface incoerente.

## What Changes

- Scaffold da aplicação React com Vite e TypeScript
- **Design system**: paleta de cores, escala tipográfica, espaçamentos e tokens, com suporte a tema claro e escuro
- **Componentes base**: botão, campo de formulário, seleção, tabela, cartão, modal, aviso, indicador de carregamento e estado vazio
- **Layout da aplicação**: cabeçalho, navegação lateral e área de conteúdo, responsivo
- **Cliente HTTP** tipado, com tratamento centralizado de erro e exibição de mensagens ao usuário
- **Roteamento** com as rotas de todas as telas previstas, ainda como páginas vazias
- Sem tela de login — o sistema é aberto

## Capabilities

### New Capabilities
- `frontend-shell`: aplicação React, roteamento, layout e navegação
- `design-system`: tokens visuais, temas e biblioteca de componentes base
- `api-client`: camada tipada de comunicação com o backend e tratamento de erros

### Modified Capabilities
Nenhuma — todas as capacidades são novas.

## Impact

- **Novo**: todo o diretório `frontend/`
- **Dependências**: React, TypeScript, Vite, biblioteca de roteamento e de requisições HTTP
- **Consome**: os endpoints definidos em `add-data-ingestion` e `add-simulation-api`
- **Bloqueia**: as changes de telas dependem destes componentes e deste layout

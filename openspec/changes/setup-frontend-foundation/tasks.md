## 1. Scaffold

- [x] 1.1 Inicializar o projeto em `frontend/` com Vite, React e TypeScript
- [x] 1.2 Configurar TypeScript em modo estrito e o linter
- [x] 1.3 Configurar a URL base da API por variável de ambiente
- [x] 1.4 Definir a estrutura `src/{pages,components,styles,api,hooks}`
- [x] 1.5 Criar `frontend/README.md` com instruções de execução e build

## 2. Tokens visuais

- [x] 2.1 Definir a paleta de cores para tema claro e escuro, com contraste verificado no nível AA
- [x] 2.2 Definir a escala tipográfica priorizando legibilidade de tabelas e datas
- [x] 2.3 Definir a escala de espaçamentos, raios de borda e sombras
- [x] 2.4 Expor os tokens como variáveis CSS consumíveis por todos os componentes

## 3. Tema

- [x] 3.1 Detectar a preferência de tema do sistema operacional na primeira visita
- [x] 3.2 Implementar o controle de alternância manual no cabeçalho
- [x] 3.3 Persistir a escolha do usuário entre visitas
- [x] 3.4 Verificar contraste de todos os tokens nos dois temas

## 4. Componentes base

- [x] 4.1 Implementar botão com as variantes primária, secundária e destrutiva, incluindo estado de carregamento
- [x] 4.2 Implementar campo de texto, campo numérico e seleção, com rótulo, mensagem de erro e estado desabilitado
- [x] 4.3 Implementar seletor de data e seletor de intervalo de datas
- [x] 4.4 Implementar tabela com cabeçalho fixo, ordenação e rolagem horizontal contida no próprio contêiner
- [x] 4.5 Implementar cartão e modal
- [x] 4.6 Implementar aviso nas variantes informação, sucesso, alerta e erro
- [x] 4.7 Implementar indicador de carregamento e componente de estado vazio com mensagem e ação sugerida
- [x] 4.8 Garantir indicador de foco visível e navegabilidade por teclado em todos os componentes interativos

## 5. Layout e navegação

- [x] 5.1 Implementar o layout com cabeçalho, navegação lateral e área de conteúdo
- [x] 5.2 Agrupar a navegação entre as seções de dados e de simulação
- [x] 5.3 Destacar o item de navegação correspondente à rota ativa
- [x] 5.4 Adaptar o layout para larguras reduzidas, sem sobreposição nem rolagem horizontal da página

## 6. Roteamento

- [x] 6.1 Configurar o roteador e registrar todas as rotas previstas como páginas vazias
- [x] 6.2 Implementar a página de rota não encontrada com caminho de volta à tela inicial
- [x] 6.3 Garantir que o acesso direto por URL carregue a tela correspondente

## 7. Cliente de API

- [x] 7.1 Implementar o cliente HTTP com a URL base configurável
- [x] 7.2 Definir os tipos TypeScript correspondentes aos contratos do backend
- [x] 7.3 Implementar o tratamento centralizado de erros, traduzindo respostas em mensagens ao usuário
- [x] 7.4 Tratar separadamente erro de validação, recurso não encontrado e servidor indisponível
- [x] 7.5 Implementar upload de arquivo com acompanhamento de progresso e leitura do relatório de importação
- [x] 7.6 Implementar o acompanhamento por consulta periódica de operações assíncronas, encerrando ao concluir ou falhar

## 8. Verificação

- [x] 8.1 Rodar o servidor de desenvolvimento e navegar por todas as rotas registradas
- [x] 8.2 Verificar o build de produção sem erros de compilação ou tipagem
- [x] 8.3 Alternar entre tema claro e escuro e conferir legibilidade em ambos
- [x] 8.4 Percorrer a interface usando apenas o teclado, confirmando foco visível em todos os controles
- [x] 8.5 Reduzir a janela à largura de dispositivo móvel e confirmar ausência de rolagem horizontal da página
- [x] 8.6 Desligar o backend e confirmar que a interface exibe mensagem de servidor indisponível com opção de tentar novamente

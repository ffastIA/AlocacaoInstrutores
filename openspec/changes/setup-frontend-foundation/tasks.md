## 1. Scaffold

- [ ] 1.1 Inicializar o projeto em `frontend/` com Vite, React e TypeScript
- [ ] 1.2 Configurar TypeScript em modo estrito e o linter
- [ ] 1.3 Configurar a URL base da API por variável de ambiente
- [ ] 1.4 Definir a estrutura `src/{pages,components,styles,api,hooks}`
- [ ] 1.5 Criar `frontend/README.md` com instruções de execução e build

## 2. Tokens visuais

- [ ] 2.1 Definir a paleta de cores para tema claro e escuro, com contraste verificado no nível AA
- [ ] 2.2 Definir a escala tipográfica priorizando legibilidade de tabelas e datas
- [ ] 2.3 Definir a escala de espaçamentos, raios de borda e sombras
- [ ] 2.4 Expor os tokens como variáveis CSS consumíveis por todos os componentes

## 3. Tema

- [ ] 3.1 Detectar a preferência de tema do sistema operacional na primeira visita
- [ ] 3.2 Implementar o controle de alternância manual no cabeçalho
- [ ] 3.3 Persistir a escolha do usuário entre visitas
- [ ] 3.4 Verificar contraste de todos os tokens nos dois temas

## 4. Componentes base

- [ ] 4.1 Implementar botão com as variantes primária, secundária e destrutiva, incluindo estado de carregamento
- [ ] 4.2 Implementar campo de texto, campo numérico e seleção, com rótulo, mensagem de erro e estado desabilitado
- [ ] 4.3 Implementar seletor de data e seletor de intervalo de datas
- [ ] 4.4 Implementar tabela com cabeçalho fixo, ordenação e rolagem horizontal contida no próprio contêiner
- [ ] 4.5 Implementar cartão e modal
- [ ] 4.6 Implementar aviso nas variantes informação, sucesso, alerta e erro
- [ ] 4.7 Implementar indicador de carregamento e componente de estado vazio com mensagem e ação sugerida
- [ ] 4.8 Garantir indicador de foco visível e navegabilidade por teclado em todos os componentes interativos

## 5. Layout e navegação

- [ ] 5.1 Implementar o layout com cabeçalho, navegação lateral e área de conteúdo
- [ ] 5.2 Agrupar a navegação entre as seções de dados e de simulação
- [ ] 5.3 Destacar o item de navegação correspondente à rota ativa
- [ ] 5.4 Adaptar o layout para larguras reduzidas, sem sobreposição nem rolagem horizontal da página

## 6. Roteamento

- [ ] 6.1 Configurar o roteador e registrar todas as rotas previstas como páginas vazias
- [ ] 6.2 Implementar a página de rota não encontrada com caminho de volta à tela inicial
- [ ] 6.3 Garantir que o acesso direto por URL carregue a tela correspondente

## 7. Cliente de API

- [ ] 7.1 Implementar o cliente HTTP com a URL base configurável
- [ ] 7.2 Definir os tipos TypeScript correspondentes aos contratos do backend
- [ ] 7.3 Implementar o tratamento centralizado de erros, traduzindo respostas em mensagens ao usuário
- [ ] 7.4 Tratar separadamente erro de validação, recurso não encontrado e servidor indisponível
- [ ] 7.5 Implementar upload de arquivo com acompanhamento de progresso e leitura do relatório de importação
- [ ] 7.6 Implementar o acompanhamento por consulta periódica de operações assíncronas, encerrando ao concluir ou falhar

## 8. Verificação

- [ ] 8.1 Rodar o servidor de desenvolvimento e navegar por todas as rotas registradas
- [ ] 8.2 Verificar o build de produção sem erros de compilação ou tipagem
- [ ] 8.3 Alternar entre tema claro e escuro e conferir legibilidade em ambos
- [ ] 8.4 Percorrer a interface usando apenas o teclado, confirmando foco visível em todos os controles
- [ ] 8.5 Reduzir a janela à largura de dispositivo móvel e confirmar ausência de rolagem horizontal da página
- [ ] 8.6 Desligar o backend e confirmar que a interface exibe mensagem de servidor indisponível com opção de tentar novamente

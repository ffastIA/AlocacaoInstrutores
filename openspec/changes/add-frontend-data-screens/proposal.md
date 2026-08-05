## Why

Toda simulação depende de dados corretos: instrutores com sua disponibilidade real, tipologias com carga horária configurada e turmas em andamento refletindo a situação atual. Sem interface, a equipe de mobilização dependeria do Swagger para alimentar o sistema — o que não é viável.

O momento mais crítico é a **importação de planilha**: se um erro de preenchimento não for comunicado com clareza, o usuário importa dados errados e confia numa simulação inválida.

## What Changes

- **Tela de importação**: upload das planilhas, download dos modelos e relatório de resultado destacando linhas rejeitadas e alertas
- **Tela de instrutores**: listagem com filtros por projeto e tipologia, e edição da disponibilidade
- **Tela de tipologias**: configuração de carga horária total e horas por encontro, com destaque para as pendentes que bloqueiam a simulação
- **Tela de projetos**: cadastro e consulta
- **Tela de situação atual**: turmas em andamento, com cadastro e edição
- **Tela de datas não letivas**: calendário de feriados, recessos e férias, com aviso explícito de que ainda não impactam o cálculo

## Capabilities

### New Capabilities
- `import-screen`: interface de upload, download de modelos e leitura do relatório de importação
- `registry-screens`: telas de instrutores, tipologias e projetos
- `current-state-screen`: tela das turmas em andamento
- `non-teaching-dates-screen`: tela do calendário de datas sem aula

### Modified Capabilities
Nenhuma — todas as capacidades são novas.

## Impact

- **Novo**: páginas e componentes em `frontend/src/pages/dados/`
- **Consome**: os endpoints de `add-data-ingestion` e `add-non-teaching-dates`
- **Usa**: os componentes base e o layout de `setup-frontend-foundation`
- **Habilita**: sem estas telas, a equipe não consegue alimentar o sistema para simular

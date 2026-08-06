## Why

É aqui que a ferramenta entrega seu valor. A equipe de mobilização precisa ver, de forma direta, **a partir de que data pode divulgar turma de cada tipologia** — e comparar arranjos diferentes para escolher o que melhor aproveita a equipe.

O mapa de oportunidades é a tela central do sistema: responde à pergunta que motivou o projeto. As demais telas existem para configurar o que o alimenta e para interpretar o resultado.

## What Changes

- **Tela de cenários**: criação, edição e duplicação, com período simulado, escopo de projetos, alternância de compartilhamento entre projetos e ajuste dos pesos do objetivo
- **Execução com acompanhamento**: disparo da simulação e feedback de andamento até a conclusão
- **Mapa de oportunidades**: tela principal, apresentando por tipologia e data quais turmas podem ser abertas e com quais instrutores
- **Agenda por instrutor**: ocupação ao longo do período, distinguindo turmas em andamento das sugeridas, com a capacidade ainda livre
- **Painel de indicadores**: ociosidade, equilíbrio de carga e de tipologias, e utilização por instrutor
- **Comparação de cenários**: indicadores de várias simulações lado a lado
- **Histórico**: simulações executadas, com acesso aos respectivos resultados
- **Exportação** do resultado em planilha

## Capabilities

### New Capabilities
- `scenario-screen`: configuração de cenários e ajuste dos pesos do objetivo
- `simulation-run-screen`: disparo e acompanhamento da execução
- `opportunity-map-screen`: visualização das oportunidades de abertura por tipologia e data
- `instructor-schedule-screen`: agenda de ocupação por instrutor
- `metrics-dashboard`: painel de indicadores da simulação
- `comparison-screen`: comparação de cenários e histórico de simulações

### Modified Capabilities
Nenhuma — todas as capacidades são novas.

## Impact

- **Novo**: páginas e componentes em `frontend/src/pages/simulacao/`
- **Consome**: os endpoints de `add-simulation-api`
- **Usa**: os componentes base e o layout de `setup-frontend-foundation`
- **Conclui**: com esta change o fluxo completo fica utilizável pela equipe de mobilização

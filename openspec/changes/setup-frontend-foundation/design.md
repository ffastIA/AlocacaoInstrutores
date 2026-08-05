## Context

O usuário final é a equipe de mobilização, sem perfil técnico. A ferramenta é interna, usada em desktop, para uma tarefa de planejamento — não é um produto público nem precisa de identidade visual elaborada.

O conteúdo central são **tabelas densas e linhas do tempo**: mapa de oportunidades por tipologia, agenda de ocupação por instrutor, comparação de KPIs. Isso define as prioridades visuais: legibilidade de dados tabulares acima de sofisticação estética.

## Goals / Non-Goals

**Goals:**
- Base visual coerente que as telas seguintes apenas consomem
- Legibilidade de tabelas densas e datas
- Erros da API comunicados em linguagem que a equipe entenda
- Acessibilidade por teclado e contraste adequado

**Non-Goals:**
- Telas de negócio (changes seguintes)
- Identidade visual de marca
- Otimização para dispositivo móvel além do layout não quebrar
- Internacionalização — a interface é em português

## Decisions

### Vite com React e TypeScript
Build rápido, configuração mínima, tipagem em toda a camada de dados. TypeScript importa especialmente aqui porque os contratos da API têm muitos campos e a divergência silenciosa entre frontend e backend seria difícil de detectar numa ferramenta usada esporadicamente.

### Design system próprio e enxuto em vez de biblioteca de componentes
O conjunto necessário é pequeno e específico. Adotar uma biblioteca completa traria peso e um conjunto de convenções visuais a contornar. Uma camada própria de tokens mais dez componentes base cobre o escopo e mantém total controle sobre a apresentação de tabelas — que é o ponto crítico. *Alternativa considerada:* biblioteca pronta — descartada pelo custo de customização em relação ao tamanho real do escopo.

### Tokens antes de componentes
Cores, tipografia e espaçamentos são definidos primeiro; nenhum componente usa valor literal. Sem essa disciplina, ajustar a aparência depois exigiria varrer todos os arquivos.

### Tema claro e escuro desde o início
Retrofit de tema escuro é caro porque exige revisar cada cor já escrita. Definir os dois desde o início custa pouco: são dois conjuntos de valores para os mesmos tokens.

### Rolagem horizontal dentro do contêiner da tabela
O mapa de oportunidades e a agenda por instrutor são largos por natureza. A rolagem lateral acontece dentro do contêiner da tabela, nunca no corpo da página — rolagem horizontal da página inteira desorienta e esconde a navegação.

### Tratamento de erro centralizado
Todo erro passa por um único ponto que traduz a resposta do backend em mensagem para o usuário. A API já retorna mensagens em português voltadas ao operador; o cliente as exibe sem expor status HTTP nem estrutura da resposta.

### Polling encapsulado no cliente
O acompanhamento de simulações em execução fica na camada de acesso à API, não nas telas. A tela apenas consome um estado que evolui de "executando" para "concluída".

### Rotas criadas vazias desde já
Todas as rotas previstas são registradas nesta change como páginas vazias. A navegação fica navegável do início, e as changes de tela apenas preenchem o conteúdo, sem mexer no roteamento.

## Risks / Trade-offs

- **Design system próprio exige manutenção** → mitigado pelo escopo enxuto e pela ausência de requisitos visuais sofisticados
- **Componentes definidos antes de as telas existirem podem não servir** → mitigado por derivá-los das telas já especificadas no plano; ajustes pontuais durante as changes de tela são esperados e baratos
- **Tabelas muito largas continuam difíceis de ler mesmo com rolagem** → as changes de tela avaliarão colunas fixas ou visualizações alternativas conforme a necessidade real

## Migration Plan

Não aplicável — código novo.

## Open Questions

- Confirmar se a equipe usa exclusivamente desktop ou se há necessidade real de uso em tablet
- Avaliar, durante as telas de simulação, se o mapa de oportunidades exige uma visualização de linha do tempo dedicada em vez de tabela

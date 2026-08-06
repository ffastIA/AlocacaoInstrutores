## Context

Todas as datas do domínio (período de cenário, datas de início/término de turma, data de execução de simulação, datas não letivas etc.) chegam do backend como string ISO (`YYYY-MM-DD` para datas puras, `YYYY-MM-DDTHH:mm:ss` para timestamps). Hoje cada tela decide por conta própria como exibir isso: a maioria interpola a string crua; duas telas (`PainelIndicadores.tsx`, `HistoricoPage.tsx`, `ComparacaoPage.tsx`) usam `.slice(0, 16).replace("T", " ")` para cortar o timestamp; uma tela (`LinhaDoTempoOportunidades.tsx`) já tem uma função local `formatarData` que produz dd/mm/aaaa corretamente. Não existe utilitário compartilhado de data em `frontend/src/`.

## Goals / Non-Goals

**Goals:**
- Um único ponto de formatação de data (puro texto, sem interferir nos `<input type="date">`) reaproveitado em toda a interface.
- Zero mudança de comportamento além da forma de exibição — mesma informação, mesma ordenação, mesmos dados.

**Non-Goals:**
- Internacionalização (múltiplos formatos por locale) — o produto é de uso interno em português do Brasil; um formato fixo é suficiente, sem necessidade de `Intl`/config de locale.
- Mudar o formato de datas em `<input type="date">` — esses continuam ISO, que é o contrato nativo do HTML.
- Mudar a ordenação de colunas por data — comparação lexicográfica de string ISO já produz a ordem cronológica correta; não há motivo para tocar nisso.

## Decisions

### Formatação por manipulação de string, não por `Date`/`Intl`
O utilitário novo (`frontend/src/utils/data.ts`) formata `YYYY-MM-DD` reorganizando os componentes da própria string (`slice`/`split`/`join`), sem construir um objeto `Date` a partir da data pura. É a mesma técnica já usada em `LinhaDoTempoOportunidades.tsx`.

**Por quê**: `new Date("2026-08-06")` é interpretado como meia-noite UTC. Ao formatar esse objeto de volta com `.toLocaleDateString()` (que usa o fuso horário local do navegador), em qualquer fuso horário do Brasil (UTC-3) o resultado é um dia a menos ("05/08/2026"). Isso é uma pegadinha clássica de `Date` em JavaScript com datas puras (sem componente de hora). Formatar diretamente a string ISO evita esse bug de raiz, sem precisar normalizar fuso horário em lugar nenhum.

Para timestamps (`YYYY-MM-DDTHH:mm:ss`), o mesmo princípio se aplica: extrai-se data e hora da própria string, sem passar por `Date`.

### Duas funções, não uma com parâmetro opcional
`formatarData(iso: string | null | undefined): string` e `formatarDataHora(iso: string | null | undefined): string`, em vez de uma função só com um `boolean incluirHora`. São usadas em contextos visualmente distintos (célula de tabela vs. metadado com hora) e manter as assinaturas separadas deixa o call site autoexplicativo, seguindo o padrão do projeto de nomes de função descritivos em vez de flags booleanas.

Ambas retornam `"—"` quando `iso` é `null`/`undefined`, único tratamento de ausência de dado já usado em outras colunas do projeto (ex.: `primeira_data_livre` em `PainelIndicadores.tsx`), para consistência visual.

### Escopo não inclui os `valorOrdenacao` de colunas ordenáveis
Colunas com `ordenavel: true` continuam comparando a string ISO original (`valorOrdenacao`), não a formatada — ordenação lexicográfica de `YYYY-MM-DD` já é cronológica; formatar antes de ordenar (dd/mm/aaaa) quebraria a ordenação. Isso não é uma decisão nova, é a confirmação de que o campo usado para ordenar e o campo usado para exibir podem — e neste caso devem — divergir.

## Risks / Trade-offs

- **Esquecer algum ponto de exibição fora do mapeamento already feito** → mitigado por um mapeamento exaustivo já realizado por busca no código-fonte (10 arquivos, listados em `tasks.md`); a verificação manual final (seção 7 de `tasks.md`) revisita cada tela.
- **Confundir campo de exibição com campo de ordenação ao editar uma coluna `ColunaTabela`** → mitigado por só tocar `renderizar`, nunca `valorOrdenacao`, em cada edição.

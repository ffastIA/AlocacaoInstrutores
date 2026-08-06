## 1. Modelo de dados e migração

- [x] 1.1 Atualizar `Turno` em `app/models/enums.py` para os 5 valores: `manha_1`, `manha_2`, `tarde_1`, `tarde_2`, `noite`
- [x] 1.2 Remover `carga_horaria_horas` e seu `CheckConstraint` de `InstrutorTurno` em `app/models/models.py`; atualizar docstrings que citavam o modelo de horas
- [x] 1.3 Criar nova revisão Alembic: `UPDATE` de `manha→manha_1` e `tarde→tarde_1` em `instrutor_turno`, `turmas_em_andamento`, `turmas_sugeridas`, `turma_sugerida_encontro`; remover coluna/constraint de carga horária via `batch_alter_table`; `downgrade()` reversível (best-effort, documentado como lossy)

## 2. Parsers de importação

- [x] 2.1 Simplificar `parse_turnos` em `app/services/importacao/campos.py` — remove suporte a carga horária e aos dois formatos posicional/explícito, mantém só a lista de slots
- [x] 2.2 Atualizar `parser_instrutores.py` removendo o plumbing de `carga_horaria_turno`
- [x] 2.3 Substituir `_alertar_sobrecarga`/`_horas_minimas` em `parser_turmas_andamento.py` por checagem de sobreposição de datas no mesmo `(instrutor, slot)` — continua como alerta, nunca rejeição
- [x] 2.4 Atualizar `app/services/importacao/modelos.py`: cabeçalhos, exemplos e orientações das planilhas-modelo `instrutores` (remove `carga_horaria_turno`, `turnos` com 5 valores) e `turmas-em-andamento` (`turno` com 5 valores)

## 3. Solver

- [x] 3.1 `app/services/solver/dados.py` — `InstrutorDados.turnos` de `dict[Turno, float]` para `frozenset[Turno]`
- [x] 3.2 `app/services/simulacao/repositorio.py` — ajustar `carregar_instrutores` para o novo formato de `turnos`
- [x] 3.3 `app/services/solver/ocupacao.py` — trocar acumulador de horas por conjunto de slots ocupados; funções de capacidade viram contagem de slots
- [x] 3.4 `app/services/solver/gerador_candidatas.py` — remover poda por "horas por encontro acima da capacidade do turno"; ajustar checagem de capacidade livre para o modelo binário
- [x] 3.5 `app/services/solver/cp_sat_model.py` — substituir a restrição de capacidade horária por `AddAtMostOne` por `(instrutor, slot, data)`; remover a restrição de teto de 4 turmas/dia
- [x] 3.6 `app/services/solver/metricas.py` — `primeira_data_livre` via `min()` entre slots (com detalhamento por slot); utilização e capacidade de reposição em contagem de slots em vez de horas

## 4. API e schemas

- [x] 4.1 `app/schemas/cadastros.py` — `InstrutorIn/Out.turnos: list[Turno]`, remover `TurnoDisponivelIn/Out`
- [x] 4.2 `app/api/cadastros.py` — ajustar `_instrutor_out`/`_aplicar_dados_instrutor` ao novo formato
- [x] 4.3 `app/schemas/simulacoes.py` — `CapacidadeInstrutorOut`/`KpisOut` com campos de slot (`slots_disponiveis`, `slots_ocupados`, detalhamento por slot da primeira data livre)
- [x] 4.4 `app/api/simulacoes.py` — ajustar `obter_capacidade_instrutores` e demais endpoints que referenciam os campos renomeados
- [x] 4.5 `app/services/exportacao/planilha_resultado.py` — verificar e renomear referências aos campos de KPI que mudaram de horas para slots

## 5. Frontend

- [x] 5.1 `frontend/src/api/types.ts` — `Turno` com 5 valores; remover `TurnoDisponivel`/`TurnoDisponivelIn`; `Instrutor.turnos: Turno[]`; renomear campos de horas para slots em `CapacidadeInstrutor` e `Kpis`
- [x] 5.2 `frontend/src/pages/dados/cadastros/InstrutoresTab.tsx` — lista de 5 slots no formulário de edição, sem campo de carga horária
- [x] 5.3 `frontend/src/pages/dados/SituacaoAtualPage.tsx` — `ROTULO_TURNO` com 5 valores no seletor de turno da turma; remover a checagem client-side de sobrecarga (`instrutoresSobrecarregados`)
- [x] 5.4 `frontend/src/pages/simulacao/resultado/MapaOportunidades.tsx` — `ROTULO_TURNO` com 5 valores
- [x] 5.5 `frontend/src/pages/simulacao/resultado/PainelIndicadores.tsx` — capacidade de reposição e utilização em slots, não horas
- [x] 5.6 `frontend/src/pages/simulacao/AgendaPage.tsx` — `ROTULO_TURNO` com 5 valores; colunas/resumo de capacidade em slots

## 6. Scripts VBS de planilha de teste

- [x] 6.1 `ScriptVB/gerar_planilhas_teste.vbs` (seção de instrutores) — remove `carga_horaria_turno`; `turnos` com os 5 valores de slot, mantendo ao menos um instrutor com `manha_1;manha_2`
- [x] 6.2 `ScriptVB/gerar_planilha_turmas_andamento.vbs` — `turno` com os 5 valores de slot; reformular o registro proposital de sobrecarga (João Souza) como sobreposição de datas no mesmo slot
- [x] 6.3 Reexecutar os dois scripts via `cscript` e reimportar contra o backend real, confirmando 8/8 aceitos em cada e o novo alerta de sobreposição aparecendo como esperado

## 7. Verificação

- [x] 7.1 Atualizar `tests/fabricas.py` (remove `carga_horaria_turno` do cabeçalho de instrutores) e reexecutar a suíte para localizar todos os pontos de quebra
- [x] 7.2 Reescrever os testes de `test_gerador_candidatas.py`, `test_cp_sat_model.py`, `test_metricas.py`, `test_import_turmas.py` (`TestSobrecarga`), `test_campos.py` (`TestParseTurnos`) para o modelo de slots
- [x] 7.3 Ajustar literais de turno/carga horária nos demais testes afetados (`test_import_instrutores.py`, `test_api_cadastros.py`, `test_models.py`, `test_gerador_encontros.py`, `test_cenario_negocio.py`, `test_api_simulacoes.py`)
- [x] 7.4 Suíte completa do backend passando
- [x] 7.5 Migração aplicada numa cópia do `data/alocacao.db`; conferir via SQL os 5 valores de turno e a ausência da coluna de carga horária
- [x] 7.6 Fluxo real via servidor rodando: planilha-modelo de instrutores com 5 slots, importação, turma em andamento em slot já ocupado no mesmo período (alerta, não rejeição), criação e execução de cenário, `capacidade-instrutores` retornando contagem de slots
- [x] 7.7 Frontend: `tsc --noEmit` e `npm run build` limpos; teste ao vivo de Cadastros/Instrutores, Situação Atual, execução de simulação, Agenda/Indicadores/Mapa sem resquício de "horas disponíveis"
- [x] 7.8 Exportar uma simulação real e conferir os cabeçalhos da planilha exportada

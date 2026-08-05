## 1. Parser

- [ ] 1.1 Implementar `parser_datas_nao_letivas.py` reutilizando o leitor de planilha e a normalização de cabeçalhos
- [ ] 1.2 Interpretar datas no formato `DD/MM/AAAA`, rejeitando formatos inválidos
- [ ] 1.3 Tratar `data_fim` ausente como intervalo de um único dia
- [ ] 1.4 Aplicar o tipo padrão `feriado` quando a coluna não for informada
- [ ] 1.5 Resolver o projeto por nome, aceitando vazio como aplicável a todos

## 2. Validação

- [ ] 2.1 Rejeitar linha cuja data de término seja anterior à de início
- [ ] 2.2 Rejeitar linha que referencie projeto inexistente
- [ ] 2.3 Emitir alerta para intervalos que cobrem apenas sextas-feiras ou fins de semana
- [ ] 2.4 Aceitar intervalos sobrepostos sem consolidar registros

## 3. Endpoints

- [ ] 3.1 Implementar `POST /importar/datas-nao-letivas` retornando o relatório de validação
- [ ] 3.2 Implementar CRUD `/datas-nao-letivas` com filtro por intervalo e por projeto
- [ ] 3.3 Adicionar o tipo `datas-nao-letivas` ao endpoint de planilhas-modelo
- [ ] 3.4 Incluir, nas respostas de importação e consulta, o aviso de que os dados ainda não impactam o cálculo

## 4. Verificação

- [ ] 4.1 Testar importação de dia único e de intervalo
- [ ] 4.2 Testar rejeição por data de término anterior à de início
- [ ] 4.3 Testar rejeição por projeto inexistente e aceitação de projeto vazio
- [ ] 4.4 Testar alerta para feriado em fim de semana e em sexta-feira
- [ ] 4.5 Testar consulta por período retornando os intervalos que interseccionam a janela
- [ ] 4.6 Testar que uma simulação com feriados cadastrados produz o mesmo resultado que uma base sem eles, confirmando a ausência de efeito na v1

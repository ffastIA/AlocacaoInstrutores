' ============================================================================
' Gera a planilha de teste "modelo_turmas_em_andamento.xlsx" para o Sistema
' de Alocacao de Instrutores, com 8 registros de exemplo.
'
' Os instrutores e tipologias referenciados sao os mesmos gerados por
' "gerar_planilhas_teste.vbs" (modelo_instrutores.xlsx) — importe primeiro os
' instrutores e configure a carga horaria das tipologias antes de importar
' esta planilha, ou o backend rejeitara as linhas por instrutor/tipologia
' inexistente.
'
' turno usa os 5 slots de horario: manha_1, manha_2, tarde_1, tarde_2, noite.
'
' Os dois registros de Joao Souza sao proposital: ele so tem o slot "noite",
' e as duas turmas tem periodos sobrepostos (20/07-20/09 e 01/09-15/10) —
' serve para demonstrar o alerta de sobreposicao de slot na importacao, sem
' que a linha seja rejeitada (o sistema aceita e sinaliza, nao bloqueia).
'
' O arquivo eh salvo em ASCII puro de proposito: os acentos sao montados via
' ChrW() abaixo, para o texto nao depender de como o Windows decide interpretar
' a codificacao do .vbs.
'
' Como usar: de duplo clique neste arquivo (ou rode "cscript gerar_planilha_turmas_andamento.vbs"
' num terminal). O Excel precisa estar instalado. O arquivo eh salvo na
' mesma pasta deste script.
' ============================================================================

Dim cC, cA, cO
cC = ChrW(231) ' c cedilha (c)
cA = ChrW(227) ' a til (a)
cO = ChrW(243) ' o agudo (o)

Dim fso, pastaScript, caminho
Set fso = CreateObject("Scripting.FileSystemObject")
pastaScript = fso.GetParentFolderName(WScript.ScriptFullName)
caminho = pastaScript & "\modelo_turmas_em_andamento.xlsx"

Dim excel
Set excel = CreateObject("Excel.Application")
excel.Visible = False
excel.DisplayAlerts = False

GerarPlanilhaTurmasAndamento excel, caminho

excel.Quit
Set excel = Nothing

WScript.Echo "Planilha gerada com sucesso:" & vbCrLf & caminho

' ----------------------------------------------------------------------------
Sub GerarPlanilhaTurmasAndamento(excel, caminho)
    Dim cabecalhos, dados
    cabecalhos = Array("instrutor", "tipologia", "modalidade", "turno", _
                        "data_inicio", "data_fim_prevista", "codigo_turma")

    ' modalidade: regular_seg_qua, regular_ter_qui ou intensiva_seg_qui.
    ' turno precisa estar entre os slots disponiveis do instrutor na
    ' planilha de instrutores (manha_1, manha_2, tarde_1, tarde_2, noite).
    dados = Array( _
        Array("Maria Silva",    "Programa" & cC & cA & "o", "regular_seg_qua",  "manha_1", "01/06/2026", "30/08/2026", "PROG-2026-014"), _
        Array("Jo" & cA & "o Souza", "Rob" & cO & "tica",   "intensiva_seg_qui", "noite", "20/07/2026", "20/09/2026", "ROB-2026-008"), _
        Array("Jo" & cA & "o Souza", "Rob" & cO & "tica",   "regular_ter_qui",  "noite", "01/09/2026", "15/10/2026", "ROB-2026-011"), _
        Array("Ana Costa",      "Rob" & cO & "tica",        "regular_seg_qua",  "manha_1", "01/06/2026", "28/08/2026", "ROB-2026-009"), _
        Array("Carlos Pereira", "Pixel Art",                "regular_ter_qui",  "tarde_1", "10/06/2026", "05/09/2026", "PXA-2026-005"), _
        Array("Beatriz Lima",   "Programa" & cC & cA & "o", "intensiva_seg_qui", "manha_2", "01/06/2026", "30/08/2026", "PROG-2026-015"), _
        Array("Felipe Santos",  "Pixel Art",                "regular_seg_qua",  "tarde_1", "15/06/2026", "10/09/2026", "PXA-2026-006"), _
        Array("Rafael Nunes",   "Rob" & cO & "tica",        "intensiva_seg_qui", "noite", "01/06/2026", "31/08/2026", "ROB-2026-010") _
    )

    Dim livro, aba, coluna, linha

    Set livro = excel.Workbooks.Add
    Set aba = livro.Sheets(1)
    aba.Name = "Dados"

    For coluna = 0 To UBound(cabecalhos)
        aba.Cells(1, coluna + 1).Value = cabecalhos(coluna)
        aba.Cells(1, coluna + 1).Font.Bold = True
    Next

    For linha = 0 To UBound(dados)
        For coluna = 0 To UBound(dados(linha))
            ' Forca texto para preservar datas como DD/MM/AAAA em vez de serem
            ' reinterpretadas pelo Excel como data nativa da celula.
            aba.Cells(linha + 2, coluna + 1).NumberFormat = "@"
            aba.Cells(linha + 2, coluna + 1).Value = dados(linha)(coluna)
        Next
    Next

    aba.Columns.AutoFit

    Dim i
    For i = livro.Sheets.Count To 2 Step -1
        livro.Sheets(i).Delete
    Next

    livro.SaveAs caminho, 51 ' 51 = xlOpenXMLWorkbook (.xlsx)
    livro.Close False
End Sub

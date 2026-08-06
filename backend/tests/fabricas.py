"""Geração de planilhas de teste em memória."""

import csv
import io

from openpyxl import Workbook


def csv_bytes(cabecalhos: list[str], linhas: list[list[str]]) -> bytes:
    """Monta um CSV com separador de coluna vírgula.

    O ponto e vírgula é reservado aos campos multivalorados dentro das células.
    """
    buffer = io.StringIO()
    escritor = csv.writer(buffer, delimiter=",", lineterminator="\n")
    escritor.writerow(cabecalhos)
    escritor.writerows(linhas)
    return buffer.getvalue().encode("utf-8")


def xlsx_bytes(cabecalhos: list[str], linhas: list[list[object]]) -> bytes:
    workbook = Workbook()
    aba = workbook.active
    aba.append(cabecalhos)
    for linha in linhas:
        aba.append(linha)
    buffer = io.BytesIO()
    workbook.save(buffer)
    return buffer.getvalue()


CABECALHOS_INSTRUTORES = [
    "nome",
    "projeto",
    "turnos",
    "dias_semana",
    "tipologias",
]


def planilha_instrutores(linhas: list[list[str]]) -> bytes:
    return csv_bytes(CABECALHOS_INSTRUTORES, linhas)


CABECALHOS_TIPOLOGIAS = ["tipologia", "carga_horaria_total", "horas_por_encontro"]


def planilha_tipologias(linhas: list[list[str]]) -> bytes:
    return csv_bytes(CABECALHOS_TIPOLOGIAS, linhas)


CABECALHOS_TURMAS = [
    "instrutor",
    "tipologia",
    "modalidade",
    "turno",
    "data_inicio",
    "data_fim_prevista",
]


def planilha_turmas(linhas: list[list[str]]) -> bytes:
    return csv_bytes(CABECALHOS_TURMAS, linhas)


CABECALHOS_DATAS_NAO_LETIVAS = ["data_inicio", "data_fim", "descricao", "tipo", "projeto"]


def planilha_datas_nao_letivas(linhas: list[list[str]]) -> bytes:
    return csv_bytes(CABECALHOS_DATAS_NAO_LETIVAS, linhas)

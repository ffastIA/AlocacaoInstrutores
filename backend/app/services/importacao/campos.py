"""Interpretação dos campos multivalorados das planilhas.

Os campos usam ponto e vírgula como separador: `manha;tarde`, `2;3;4;5`,
`Programação;Pixel Art`.
"""

from datetime import date, datetime

from app.models.enums import DIA_SEMANA_MAX, DIA_SEMANA_MIN, Turno

SEPARADOR = ";"

# Formatos aceitos nas colunas de data, em ordem de tentativa. O primeiro é o
# usado nas planilhas da equipe; os demais cobrem exportações do Excel.
FORMATOS_DATA = ("%d/%m/%Y", "%Y-%m-%d", "%d/%m/%y", "%d-%m-%Y")


class ValorInvalidoError(ValueError):
    """Um campo não pôde ser interpretado. A mensagem vai direto ao usuário."""


def parse_lista(texto: str) -> list[str]:
    """Divide por ponto e vírgula, descartando itens vazios."""
    if not texto:
        return []
    return [item.strip() for item in texto.split(SEPARADOR) if item.strip()]


def parse_turnos(texto_turnos: str, texto_cargas: str) -> list[tuple[Turno, float]]:
    """Interpreta os turnos disponíveis com sua carga horária.

    Aceita dois formatos:

    - **Explícito**: `manha:4;tarde:4` — dispensa a coluna de cargas
    - **Posicional**: `manha;tarde` com cargas `4;4` — pareado por posição

    O formato posicional falha explicitamente quando as listas têm tamanhos
    diferentes. Inferir um valor faltante produziria capacidade errada, e
    capacidade errada produz simulação errada sem nenhum sinal visível.
    """
    itens = parse_lista(texto_turnos)
    if not itens:
        raise ValorInvalidoError("Nenhum turno informado")

    if any(":" in item for item in itens):
        return _parse_turnos_explicito(itens)
    return _parse_turnos_posicional(itens, parse_lista(texto_cargas))


def _parse_turnos_explicito(itens: list[str]) -> list[tuple[Turno, float]]:
    resultado: list[tuple[Turno, float]] = []
    for item in itens:
        if ":" not in item:
            raise ValorInvalidoError(
                f"'{item}' não segue o formato 'turno:horas' usado nos demais itens"
            )
        nome, _, carga = item.partition(":")
        resultado.append((parse_turno(nome), _parse_carga(carga)))
    return _sem_duplicatas(resultado)


def _parse_turnos_posicional(itens: list[str], cargas: list[str]) -> list[tuple[Turno, float]]:
    if not cargas:
        raise ValorInvalidoError(
            "Carga horária por turno não informada. Preencha a coluna "
            "'carga_horaria_turno' ou use o formato 'manha:4;tarde:4'"
        )
    if len(itens) != len(cargas):
        raise ValorInvalidoError(
            f"{len(itens)} turno(s) informado(s) mas {len(cargas)} carga(s) horária(s): "
            "as duas listas precisam ter a mesma quantidade de itens"
        )
    return _sem_duplicatas(
        [
            (parse_turno(nome), _parse_carga(carga))
            for nome, carga in zip(itens, cargas, strict=True)
        ]
    )


def _sem_duplicatas(pares: list[tuple[Turno, float]]) -> list[tuple[Turno, float]]:
    vistos: set[Turno] = set()
    for turno, _ in pares:
        if turno in vistos:
            raise ValorInvalidoError(f"Turno '{turno.value}' informado mais de uma vez")
        vistos.add(turno)
    return pares


def parse_turno(texto: str) -> Turno:
    """Interpreta o nome de um turno, tolerando acentos e maiúsculas."""
    from app.services.importacao.leitor_planilha import normalizar_cabecalho

    canonico = normalizar_cabecalho(texto)
    try:
        return Turno(canonico)
    except ValueError:
        validos = ", ".join(t.value for t in Turno)
        raise ValorInvalidoError(f"Turno inválido: '{texto}'. Valores aceitos: {validos}") from None


def _parse_carga(texto: str) -> float:
    try:
        valor = float(texto.strip().replace(",", "."))
    except ValueError:
        raise ValorInvalidoError(f"Carga horária inválida: '{texto}'") from None
    if valor <= 0:
        raise ValorInvalidoError(f"Carga horária deve ser maior que zero: '{texto}'")
    return valor


def parse_dias_semana(texto: str) -> list[int]:
    """Interpreta os dias disponíveis: 2 = segunda ... 6 = sexta.

    O dia 6 é aceito e armazenado, mas conta apenas como capacidade de
    reposição — nunca recebe turma regular.
    """
    itens = parse_lista(texto)
    if not itens:
        raise ValorInvalidoError("Nenhum dia da semana informado")

    dias: list[int] = []
    for item in itens:
        try:
            dia = int(float(item))
        except ValueError:
            raise ValorInvalidoError(f"Dia da semana inválido: '{item}'") from None
        if not DIA_SEMANA_MIN <= dia <= DIA_SEMANA_MAX:
            raise ValorInvalidoError(
                f"Dia da semana fora da faixa: '{item}'. "
                f"Aceito de {DIA_SEMANA_MIN} (segunda) a {DIA_SEMANA_MAX} (sexta)"
            )
        if dia in dias:
            raise ValorInvalidoError(f"Dia da semana '{dia}' informado mais de uma vez")
        dias.append(dia)
    return sorted(dias)


def parse_data(texto: str, campo: str = "data") -> date:
    """Interpreta uma data, aceitando os formatos usuais das planilhas."""
    texto = texto.strip()
    if not texto:
        raise ValorInvalidoError(f"{campo} não informada")

    for formato in FORMATOS_DATA:
        try:
            return datetime.strptime(texto, formato).date()
        except ValueError:
            continue
    raise ValorInvalidoError(f"{campo} inválida: '{texto}'. Use o formato DD/MM/AAAA")


def parse_numero(texto: str, campo: str) -> float:
    """Interpreta um número, aceitando vírgula como separador decimal."""
    texto = texto.strip().replace(",", ".")
    if not texto:
        raise ValorInvalidoError(f"{campo} não informado")
    try:
        return float(texto)
    except ValueError:
        raise ValorInvalidoError(f"{campo} inválido: '{texto}'") from None


def parse_inteiro(texto: str, campo: str) -> int:
    """Interpreta um inteiro, recusando valores fracionários."""
    valor = parse_numero(texto, campo)
    if valor != int(valor):
        raise ValorInvalidoError(f"{campo} deve ser um número inteiro: '{texto}'")
    return int(valor)

"""Resultado de uma importação de planilha.

A validação é **por linha**: as válidas são importadas mesmo que outras falhem.
Uma planilha de 60 instrutores com um erro de digitação não deve obrigar a
equipe a reenviar tudo sem saber onde está o problema.
"""

from dataclasses import dataclass, field


@dataclass
class ErroLinha:
    """Uma linha rejeitada, com o número da linha como aparece na planilha."""

    linha: int
    motivo: str
    coluna: str | None = None

    def __str__(self) -> str:
        onde = f" (coluna '{self.coluna}')" if self.coluna else ""
        return f"Linha {self.linha}{onde}: {self.motivo}"


@dataclass
class AlertaLinha:
    """Uma linha importada com ressalva.

    Distinta de `ErroLinha`: o dado entrou. Misturar as duas faria o usuário
    reprocessar dados que já existem, ou ignorar dados que ficaram de fora.
    """

    linha: int | None
    mensagem: str

    def __str__(self) -> str:
        onde = f"Linha {self.linha}: " if self.linha else ""
        return f"{onde}{self.mensagem}"


@dataclass
class ResultadoImportacao:
    """Resumo do que entrou, do que foi recusado e do que merece atenção."""

    importados: int = 0
    atualizados: int = 0
    erros: list[ErroLinha] = field(default_factory=list)
    alertas: list[AlertaLinha] = field(default_factory=list)
    # Preenchido quando o arquivo inteiro é recusado (ex.: coluna obrigatória
    # ausente). Nesse caso nada é importado.
    erro_arquivo: str | None = None

    @property
    def total_processados(self) -> int:
        return self.importados + self.atualizados

    @property
    def rejeitados(self) -> int:
        return len(self.erros)

    @property
    def sucesso(self) -> bool:
        return self.erro_arquivo is None and not self.erros

    def adicionar_erro(self, linha: int, motivo: str, coluna: str | None = None) -> None:
        self.erros.append(ErroLinha(linha=linha, motivo=motivo, coluna=coluna))

    def adicionar_alerta(self, mensagem: str, linha: int | None = None) -> None:
        self.alertas.append(AlertaLinha(linha=linha, mensagem=mensagem))


class ArquivoInvalidoError(Exception):
    """O arquivo não pôde ser processado — nenhuma linha é importada.

    Usado para falhas estruturais: formato não suportado, planilha ilegível ou
    coluna obrigatória ausente.
    """

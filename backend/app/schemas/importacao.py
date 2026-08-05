"""Contratos de resposta das importações."""

from pydantic import BaseModel, Field

from app.services.importacao.resultado import ResultadoImportacao


class ErroLinhaOut(BaseModel):
    linha: int = Field(description="Número da linha na planilha, contando o cabeçalho")
    motivo: str
    coluna: str | None = None


class AlertaOut(BaseModel):
    linha: int | None = None
    mensagem: str


class ResultadoImportacaoOut(BaseModel):
    """Resumo da importação.

    `erros` lista o que ficou de fora; `alertas` lista o que entrou com
    ressalva. A distinção evita que o usuário reprocesse dados já importados ou
    ignore dados que faltaram.
    """

    sucesso: bool
    importados: int
    atualizados: int
    rejeitados: int
    erro_arquivo: str | None = Field(
        default=None,
        description="Preenchido quando o arquivo inteiro foi recusado; nada foi importado",
    )
    erros: list[ErroLinhaOut] = []
    alertas: list[AlertaOut] = []

    @classmethod
    def de_resultado(cls, resultado: ResultadoImportacao) -> "ResultadoImportacaoOut":
        return cls(
            sucesso=resultado.sucesso,
            importados=resultado.importados,
            atualizados=resultado.atualizados,
            rejeitados=resultado.rejeitados,
            erro_arquivo=resultado.erro_arquivo,
            erros=[
                ErroLinhaOut(linha=e.linha, motivo=e.motivo, coluna=e.coluna)
                for e in resultado.erros
            ],
            alertas=[AlertaOut(linha=a.linha, mensagem=a.mensagem) for a in resultado.alertas],
        )

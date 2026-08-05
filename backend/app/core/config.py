"""Configuração da aplicação, lida de variáveis de ambiente.

Todos os campos têm padrão adequado para execução local: a aplicação sobe sem
nenhuma variável definida.
"""

from functools import lru_cache
from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Raiz do repositório, dois níveis acima de app/core/.
# Caminhos relativos são resolvidos a partir daqui, e não do diretório de
# trabalho, para que a aplicação use sempre o mesmo banco independentemente de
# onde o comando foi disparado.
RAIZ_REPO = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_nome: str = "Alocação de Instrutores"
    app_versao: str = "0.1.0"

    database_url: str = "sqlite:///data/alocacao.db"
    cenarios_dir: Path = Path("data/cenarios")

    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
    ]

    solver_time_limit_seg: int = 180
    solver_num_workers: int = 8
    solver_gap_relativo: float = 0.02
    solver_seed: int = 42

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _dividir_origens(cls, valor: object) -> object:
        """Aceita as origens como lista JSON ou string separada por vírgula."""
        if isinstance(valor, str) and not valor.strip().startswith("["):
            return [item.strip() for item in valor.split(",") if item.strip()]
        return valor

    @property
    def caminho_banco(self) -> Path | None:
        """Caminho absoluto do arquivo SQLite, ou None se o banco não for SQLite em arquivo."""
        prefixo = "sqlite:///"
        if not self.database_url.startswith(prefixo):
            return None
        caminho = self.database_url[len(prefixo) :]
        if not caminho or caminho == ":memory:":
            return None
        return self._absoluto(Path(caminho))

    @property
    def database_url_resolvida(self) -> str:
        """URL do banco com o caminho do arquivo resolvido para absoluto."""
        caminho = self.caminho_banco
        if caminho is None:
            return self.database_url
        return f"sqlite:///{caminho.as_posix()}"

    @property
    def caminho_cenarios(self) -> Path:
        """Caminho absoluto do diretório de JSONs de parâmetros de cenário."""
        return self._absoluto(self.cenarios_dir)

    @staticmethod
    def _absoluto(caminho: Path) -> Path:
        return caminho if caminho.is_absolute() else (RAIZ_REPO / caminho).resolve()

    def garantir_diretorios(self) -> None:
        """Cria os diretórios de dados e de cenários se ainda não existirem."""
        self.caminho_cenarios.mkdir(parents=True, exist_ok=True)
        banco = self.caminho_banco
        if banco is not None:
            banco.parent.mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

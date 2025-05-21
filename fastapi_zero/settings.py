from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Configurações do aplicativo FastAPI, incluindo a URL do banco de dados.
    Esta classe herda de BaseSettings do Pydantic, permitindo o carregamento
    automático de variáveis de ambiente a partir de um arquivo .env.

    Attributes:
        model_config (SettingsConfigDict): Configurações do modelo,
        incluindo o arquivo .env e a codificação.
        DATABASE_URL (str): URL de conexão com o banco de dados.
    """

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
    )

    DATABASE_URL: str

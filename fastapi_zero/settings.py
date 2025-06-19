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
        SECRET_KEY (str): Chave secreta usada para criptografia e segurança.
        ALGORITHM (str): Algoritmo de criptografia usado para tokens.
        ACCESS_TOKEN_EXPIRE_MINUTES (int): Tempo de expiração do token
        de acesso em minutos.
        POSTGRES_USER (str): Nome de usuário do banco de dados PostgreSQL.
        POSTGRES_PASSWORD (str): Senha do banco de dados PostgreSQL.
        POSTGRES_DB (str): Nome do banco de dados PostgreSQL.
    """

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
    )

    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

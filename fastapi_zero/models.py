from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column, registry

table_registry = registry()


@table_registry.mapped_as_dataclass
class User:
    """
    Modelo de usuário para o banco de dados.
    Este modelo representa a tabela de usuários no banco de dados
    e contém os campos necessários para armazenar informações
    sobre os usuários.

    Attributes:
        id (int): ID único do usuário (chave primária).
        username (str): Nome de usuário único.
        email (str): Email único do usuário.
        password (str): Senha do usuário.
        created_at (datetime): Timestamp de criação do usuário.
        updated_at (datetime): Timestamp da última atualização do usuário.
    """

    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now(), onupdate=func.now()
    )

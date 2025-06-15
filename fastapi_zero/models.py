from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, registry, relationship

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
        todos (List[Todo]): Lista de tarefas associadas ao usuário.
        Isso serve para vincular as tarefas a um usuário específico.
        Esta lista é carregada com o relacionamento 'selectin' para
        otimizar as consultas e evitar o carregamento excessivo de dados.
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
    todos: Mapped[List[Todo]] = relationship(
        init=False,
        cascade='all, delete-orphan',
        lazy='selectin',
    )


class TodoState(str, Enum):
    """
    Enum para representar os estados de uma tarefa (Todo).
    Esta enumeração define os possíveis estados de uma tarefa,
    permitindo que as tarefas sejam categorizadas de forma clara.

    Attributes:
        draft (str): Tarefa em rascunho.
        todo (str): Tarefa pendente.
        doing (str): Tarefa em andamento.
        done (str): Tarefa concluída.
        trash (str): Tarefa na lixeira.
    """

    draft = 'draft'
    todo = 'todo'
    doing = 'doing'
    done = 'done'
    trash = 'trash'


@table_registry.mapped_as_dataclass
class Todo:
    """
    Modelo de tarefa (Todo) para o banco de dados.
    Este modelo representa a tabela de tarefas no banco de dados
    e contém os campos necessários para armazenar informações
    sobre as tarefas.

    Attributes:
        id (int): ID único da tarefa (chave primária).
        title (str): Título da tarefa.
        description (str): Descrição da tarefa.
        state (TodoState): Estado atual da tarefa.
        user_id (int): ID do usuário associado à tarefa (chave estrangeira),
        isso serve para vincular a tarefa a um usuário específico.
        created_at (datetime): Timestamp de criação da tarefa.
        updated_at (datetime): Timestamp da última atualização da tarefa.
    """

    __tablename__ = 'todos'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    title: Mapped[str]
    description: Mapped[str]
    state: Mapped[TodoState]
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    created_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now(), onupdate=func.now()
    )

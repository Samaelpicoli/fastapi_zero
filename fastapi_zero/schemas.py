from datetime import datetime
from typing import List

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from fastapi_zero.models import TodoState


class Message(BaseModel):
    """
    Modelo para representar uma mensagem.

    Attributes:
        message (str): O conteúdo da mensagem
    """

    message: str


class UserSchema(BaseModel):
    """
    Modelo para representar a criação de um usuário.

    Attributes:
        username (str): O nome de usuário
        email (str): O endereço de e-mail do usuário
        password (str): A senha do usuário
    """

    username: str
    email: EmailStr
    password: str


class UserPublic(BaseModel):
    """
    Modelo para representar uma resposta quando é criado o usuário,
    sem expor a senha.

    Attributes:
        id (int): O ID do usuário
        username (str): O nome de usuário
        email (str): O endereço de e-mail do usuário
        model_config (ConfigDict): Configuração do modelo
        Esta configuração permite que o modelo seja criado a partir de
        atributos, o que é útil para criar instâncias do modelo a partir
        de dicionários ou outros objetos que possuem os mesmos atributos.
    """

    id: int
    username: str
    email: EmailStr
    model_config = ConfigDict(from_attributes=True)


class UserList(BaseModel):
    """
    Modelo para representar uma lista de usuários a partir do Schema
    UserPublic.
    """

    users: list[UserPublic]


class Token(BaseModel):
    """
    Modelo para representar um token JWT.
    Utilizado para autenticação e autorização de usuários.

    Attributes:
        access_token (str): O token de acesso JWT
        token_type (str): O tipo do token, geralmente 'bearer'
    """

    access_token: str
    token_type: str


class FilterPage(BaseModel):
    """
    Modelo para representar filtros de paginação.

    Attributes:
        offset (int): O deslocamento para a paginação, deve ser
        maior ou igual a 0
        limit (int): O número máximo de itens por página, deve ser
        maior ou igual a 0
    """

    offset: int = Field(ge=0, default=0)
    limit: int = Field(ge=0, default=10)


class FilterTodo(FilterPage):
    """
    Modelo para representar filtros de paginação específicos para
    objetos Todo.

    Attributes:
        title (str | None): O título do todo, opcional e deve ter
        no mínimo 3 caracteres
        description (str | None): A descrição do todo, opcional
        state (TodoState | None): O estado do todo, opcional
    """

    title: str | None = Field(default=None, min_length=3)
    description: str | None = None
    state: TodoState | None = None


class TodoSchema(BaseModel):
    """
    Modelo para representar a criação de um objeto Todo.

    Attributes:
        title (str): O título do todo, deve ter no mínimo 3 caracteres
        description (str): A descrição do todo
        state (TodoState): O estado do todo, padrão é 'todo'
    """

    title: str
    description: str
    state: TodoState = Field(default=TodoState.todo)


class TodoPublic(TodoSchema):
    """
    Modelo para representar um objeto Todo público, que inclui
    o ID do todo e herda de TodoSchema.

    Attributes:
        id (int): O ID do todo.
        created_at (datetime): A data de criação do todo.
        updated_at (datetime): A data da última atualização do todo.
    """

    id: int
    created_at: datetime
    updated_at: datetime


class TodoList(BaseModel):
    """
    Modelo para representar uma lista de objetos Todo.

    Attributes:
        todos (list[TodoPublic]): Lista de objetos TodoPublic
    """

    todos: List[TodoPublic]


class TodoUpdate(BaseModel):
    """
    Modelo para representar a atualização de um objeto Todo.

    Attributes:
        title (str): O título do todo
        description (str): A descrição do todo
        state (TodoState): O estado do todo.
    """

    title: str | None = None
    description: str | None = None
    state: TodoState | None = None

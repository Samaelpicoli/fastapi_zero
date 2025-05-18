from pydantic import BaseModel, EmailStr


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
    """

    id: int
    username: str
    email: EmailStr


class UserDB(UserSchema):
    """
    Modelo para representar um usuário armazenado no banco de dados.

    Attributes:
        id (int): O ID do usuário
    """

    id: int


class UserList(BaseModel):
    """
    Modelo para representar uma lista de usuários a partir do Schema
    UserPublic.
    """

    users: list[UserPublic]

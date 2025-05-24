from pydantic import BaseModel, ConfigDict, EmailStr


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

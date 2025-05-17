from pydantic import BaseModel


class Message(BaseModel):
    """
    Modelo para representar uma mensagem.

    Attributes:
        message (str): O conteúdo da mensagem
    """

    message: str

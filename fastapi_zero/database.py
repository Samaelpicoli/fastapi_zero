from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from fastapi_zero.settings import Settings

engine = create_engine(Settings().DATABASE_URL)


def get_session():
    """
    Cria uma sessão de banco de dados.
    Esta função cria uma sessão de banco de dados usando o SQLAlchemy.
    A sessão é criada com o URL do banco de dados definido nas
    configurações do aplicativo.

    Yields:
        Session: Uma sessão de banco de dados. O yield permite que
        a sessão seja usada em um contexto de gerador, garantindo
        que a sessão seja fechada corretamente após o uso.
    """
    with Session(engine) as session:
        yield session

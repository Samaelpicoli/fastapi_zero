from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from fastapi_zero.settings import Settings

engine = create_async_engine(Settings().DATABASE_URL)


async def get_session():
    """
    Cria uma sessão de banco de dados.
    Esta função cria uma sessão de banco de dados usando o SQLAlchemy.
    A sessão é criada com o URL do banco de dados definido nas
    configurações do aplicativo.
    A sessão é gerenciada de forma assíncrona para permitir
    operações não bloqueantes. Utilizando o async_session
    do SQLAlchemy, garantimos que as operações de banco de dados
    possam ser executadas de forma eficiente em um ambiente
    assíncrono. Solicitar a sessão será feito através de async e o gerenciador
    também será assíncrono, garantindo que a sessão seja fechada
    corretamente após o uso.

    Yields:
        AsyncSession: Uma sessão de banco de dados assíncrona.
        Esta função é usada como uma dependência em rotas FastAPI
        para fornecer uma sessão de banco de dados para operações CRUD.
        O yield permite que a sessão seja usada em um contexto de gerador,
        garantindo que a sessão seja fechada corretamente após o uso.
    """
    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session

from http import HTTPStatus

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from fastapi_zero.database import get_session
from fastapi_zero.models import User
from fastapi_zero.schemas import (
    Message,
    UserList,
    UserPublic,
    UserSchema,
)

app = FastAPI(title='FastAPI Zero')


@app.get('/', status_code=HTTPStatus.OK, response_model=Message)
def read_root():
    """
    Retorna uma mensagem de boas-vindas.
    Esta função manipula requisições GET para a rota raiz ('/').

    Returns:
        dict: Um dicionário contendo a mensagem 'Hello World!'
    """
    return {'message': 'Hello World!'}


@app.get('/hello', status_code=HTTPStatus.OK, response_class=HTMLResponse)
def hello_world():
    """
    Retorna uma mensagem de boas-vindas em formato HTML.
    Esta função manipula requisições GET para a rota '/hello'.

    Returns:
        dict: Um dicionário contendo a mensagem 'Hello World!'
    """
    html = """
    <html>
        <head>
            <title>FastAPI Zero</title>
        </head>
        <body>
            <h1>Hello World!</h1>
        </body>
    </html>
    """
    return HTMLResponse(content=html)


@app.get('/users/', status_code=HTTPStatus.OK, response_model=UserList)
def read_users(
    skip: int = 0, limit: int = 100, session: Session = Depends(get_session)
):
    """
    Retorna uma lista de usuários.
    Esta função manipula requisições GET para a rota '/users/'.
    Retorna uma lista de usuários com base nos parâmetros de
    paginação 'skip' e 'limit'.

    Args:
        skip (int): O número de usuários a serem pulados.
        limit (int): O número máximo de usuários a serem retornados.
        session (Session): A sessão do banco de dados.

    Returns:
        UserList: Uma lista de usuários com nome e email.
    """
    users = session.scalars(select(User).offset(skip).limit(limit)).all()
    return {'users': users}


@app.post('/users/', status_code=HTTPStatus.CREATED, response_model=UserPublic)
def create_user(user: UserSchema, session: Session = Depends(get_session)):
    """
    Cria um novo usuário.
    Esta função manipula requisições POST para a rota '/users/'.
    Retorna os dados do usuário criado.

    Args:
        user (UserSchema): Os dados do usuário a serem criados.
        session (Session): A sessão do banco de dados.

    Returns:
        UserPublic: Os dados do usuário criado.

    Raises:
        HTTPException: Se o nome de usuário ou e-mail já existirem.
    """
    db_user = session.scalar(
        select(User).where(
            (User.username == user.username) | (User.email == user.email)
        )
    )

    if db_user:
        if db_user.username == user.username:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='Username already exists',
            )
        if db_user.email == user.email:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='Email already exists',
            )

    db_user = User(
        username=user.username, password=user.password, email=user.email
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return db_user


@app.put(
    '/users/{user_id}', status_code=HTTPStatus.OK, response_model=UserPublic
)
def update_user(
    user_id: int, user: UserSchema, session: Session = Depends(get_session)
):
    """
    Atualiza os dados de um usuário específico.
    Esta função manipula requisições PUT para a rota '/users/{user_id}'.
    Retorna os dados do usuário atualizado.

    Args:
        user_id (int): O ID do usuário a ser atualizado.
        user (UserSchema): Os dados do usuário a serem atualizados.
        session (Session): A sessão do banco de dados.

    Returns:
        UserPublic: Os dados do usuário atualizado.

    Raises:
        HTTPException: Se o usuário não for encontrado ou se o
        nome de usuário ou e-mail já existirem.
    """
    user_db = session.scalar(select(User).where(User.id == user_id))
    if not user_db:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User not found'
        )

    try:
        user_db.email = user.email
        user_db.username = user.username
        user_db.password = user.password

        session.add(user_db)
        session.commit()
        session.refresh(user_db)

        return user_db

    except IntegrityError:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Username or email already exists',
        )


@app.delete(
    '/users/{user_id}', status_code=HTTPStatus.OK, response_model=Message
)
def delete_user(user_id: int, session: Session = Depends(get_session)):
    """
    Deleta um usuário específico.
    Esta função manipula requisições DELETE para a rota '/users/{user_id}'.
    Retorna uma mensagem de sucesso após a exclusão do usuário.

    Args:
        user_id (int): O ID do usuário a ser deletado.
        session (Session): A sessão do banco de dados.

    Returns:
        dict: Um dicionário contendo a mensagem de sucesso.

    Raises:
        HTTPException: Se o usuário não for encontrado.
    """
    user_db = session.scalar(select(User).where(User.id == user_id))
    if not user_db:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User not found'
        )

    session.delete(user_db)
    session.commit()

    return {'message': 'User deleted'}


@app.get('/users/{user_id}', response_model=UserPublic)
def get_user(user_id: int, session: Session = Depends(get_session)):
    """
    Retorna os dados de um usuário específico.
    Esta função manipula requisições GET para a rota '/users/{user_id}'.
    Retorna os dados do usuário correspondente ao ID fornecido.

    Args:
        user_id (int): O ID do usuário a ser retornado.
        session (Session): A sessão do banco de dados.

    Returns:
        UserPublic: Os dados do usuário.
    """
    user_db = session.scalar(select(User).where(User.id == user_id))
    if not user_db:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User not found'
        )

    return user_db

from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from fastapi_zero.database import get_session
from fastapi_zero.models import User
from fastapi_zero.schemas import (
    FilterPage,
    Message,
    UserList,
    UserPublic,
    UserSchema,
)
from fastapi_zero.security import get_current_user, get_password_hash

router = APIRouter(prefix='/users', tags=['users'])

T_Session = Annotated[Session, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.get('/', status_code=HTTPStatus.OK, response_model=UserList)
def read_users(
    session: T_Session,
    current_user: CurrentUser,
    filter_users: Annotated[FilterPage, Query()],
):
    """
    Retorna uma lista de usuários.
    Esta função manipula requisições GET para a rota '/users/'.
    Retorna uma lista de usuários com base nos parâmetros de
    paginação 'skip' e 'limit'.
    Somente usuários com login poderão acessar esta rota.

    Args:
        skip (int): O número de usuários a serem pulados.
        limit (int): O número máximo de usuários a serem retornados.
        session (Session): A sessão do banco de dados.
        current_user (User): Usuário autenticado (injetado automaticamente).

    Returns:
        UserList: Uma lista de usuários com nome e email.
    """
    users = session.scalars(
        select(User).offset(filter_users.offset).limit(filter_users.limit)
    ).all()
    return {'users': users}


@router.post('/', status_code=HTTPStatus.CREATED, response_model=UserPublic)
def create_user(user: UserSchema, session: T_Session):
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
        username=user.username,
        password=get_password_hash(user.password),
        email=user.email,
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return db_user


@router.put('/{user_id}', status_code=HTTPStatus.OK, response_model=UserPublic)
def update_user(
    user_id: int,
    user: UserSchema,
    session: T_Session,
    current_user: CurrentUser,
):
    """
    Atualiza os dados de um usuário específico.

    Permite que um usuário autenticado atualize seus próprios dados.
    O usuário só pode atualizar suas próprias informações, não podendo
    modificar dados de outros usuários.

    Args:
        user_id (int): ID do usuário a ser atualizado
        user (UserSchema): Novos dados do usuário
        session (Session): Sessão do banco de dados
        current_user (User): Usuário autenticado atual

    Returns:
        UserPublic: Dados atualizados do usuário

    Raises:
        HTTPException: Se tentar atualizar outro usuário ou
        se o username/email já existir.
    """
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='Not enough permissions',
        )

    try:
        current_user.email = user.email
        current_user.username = user.username
        current_user.password = get_password_hash(user.password)

        session.add(current_user)
        session.commit()
        session.refresh(current_user)

        return current_user

    except IntegrityError:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Username or email already exists',
        )


@router.delete('/{user_id}', status_code=HTTPStatus.OK, response_model=Message)
def delete_user(
    user_id: int,
    session: T_Session,
    current_user: CurrentUser,
):
    """
    Remove um usuário do sistema.
    Permite que um usuário autenticado remova sua própria conta.
    O usuário só pode deletar sua própria conta, não podendo
    remover outros usuários do sistema.

    Args:
        user_id (int): ID do usuário a ser removido.
        session (Session): Sessão do banco de dados.
        current_user (User): Usuário autenticado atual.

    Returns:
        Message: Dicionário com mensagem de confirmação.

    Raises:
        HTTPException: Se tentar deletar outro usuário do banco.
    """
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='Not enough permissions',
        )

    session.delete(current_user)
    session.commit()

    return {'message': 'User deleted'}


@router.get('/{user_id}', response_model=UserPublic)
def get_user(user_id: int, session: T_Session):
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

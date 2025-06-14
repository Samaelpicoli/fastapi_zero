from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_zero.database import get_session
from fastapi_zero.models import User
from fastapi_zero.schemas import Token
from fastapi_zero.security import (
    create_access_token,
    get_current_user,
    verify_password,
)

router = APIRouter(prefix='/auth', tags=['auth'])

T_Session = Annotated[AsyncSession, Depends(get_session)]
OAuth2Form = Annotated[OAuth2PasswordRequestForm, Depends()]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post('/token', response_model=Token)
async def login_for_access_token(
    form_data: OAuth2Form,
    session: T_Session,
):
    """
    Autentica um usuário e retorna um token de acesso.
    Esta função manipula requisições POST para a rota '/token'.
    Utiliza o formulário de autenticação OAuth2 para verificar as credenciais.

    Args:
        form_data (OAuth2PasswordRequestForm): O formulário contendo
        as credenciais do usuário.
        session (Session): A sessão do banco de dados.

    Returns:
        dict: Um dicionário contendo o token de acesso.

    Raises:
        HTTPException: Se as credenciais forem inválidas.
    """
    user = await session.scalar(
        select(User).where(User.email == form_data.username)
    )

    if not user:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Incorrect email or password',
        )

    if not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Incorrect email or password',
        )

    access_token = create_access_token({'sub': user.email})

    return {'access_token': access_token, 'token_type': 'Bearer'}


@router.post('/refresh/token', response_model=Token)
async def refresh_access_token(user: CurrentUser):
    """
    Atualiza o token de acesso do usuário autenticado.
    Esta função manipula requisições POST para a rota '/refresh/token'.
    Retorna um novo token de acesso para o usuário autenticado.

    Args:
        user (User): O usuário autenticado.

    Returns:
        Token: Um objeto Token contendo o novo token de acesso.
    """
    access_token = create_access_token({'sub': user.email})

    return {'access_token': access_token, 'token_type': 'Bearer'}

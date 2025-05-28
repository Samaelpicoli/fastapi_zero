from datetime import datetime, timedelta
from http import HTTPStatus
from zoneinfo import ZoneInfo

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jwt import DecodeError, decode, encode
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.orm import Session

from fastapi_zero.database import get_session
from fastapi_zero.models import User

SECRET_KEY = 'my-secret-key'
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = PasswordHash.recommended()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')


def get_password_hash(password: str) -> str:
    """
    Gera um hash da senha fornecida.
    Esta função utiliza o PasswordHash recomendado para criar um hash seguro
    da senha, com a biblioteca pwdlib.
    Esta função é útil para armazenar senhas
    de forma segura no banco de dados.

    Args:
        password (str): A senha a ser hasheada.

    Returns:
        str: O hash da senha.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica se a senha fornecida corresponde ao hash armazenado.
    Esta função utiliza o PasswordHash recomendado para verificar se a senha
    fornecida corresponde ao hash armazenado. É útil para autenticação de
    usuários, garantindo que a senha fornecida pelo usuário seja válida.

    Args:
        plain_password (str): A senha fornecida pelo usuário.
        hashed_password (str): O hash da senha armazenado.

    Returns:
        bool: True se a senha corresponder ao hash, False caso contrário.
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
    """
    Cria um token de acesso JWT com os dados fornecidos.
    Esta função gera um token JWT (JSON Web Token) que pode ser usado para
    autenticação e autorização de usuários. O token inclui uma data
    de expiração definida por ACCESS_TOKEN_EXPIRE_MINUTES, que é o
    tempo em minutos que o token será válido.

    Args:
        data (dict): Os dados a serem incluídos no token. Normalmente, isso
        inclui informações do usuário, como ID e email.

    Returns:
        str: O token de acesso JWT codificado.
    """
    to_encode = data.copy()

    expire = datetime.now(tz=ZoneInfo('UTC')) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({'exp': expire})
    encoded_jwt = encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(
    session: Session = Depends(get_session),
    token: str = Depends(oauth2_scheme),
) -> User:
    """
    Obtém e valida o usuário atual através do token JWT.
    Verifica a validade do token JWT fornecido e retorna o usuário
    correspondente do banco de dados. Esta função é usada como uma
    dependência para endpoints que requerem autenticação.

    Args:
        session (Session): Sessão do banco de dados.
        token (str): Token JWT de autenticação, obtido do header Authorization.

    Returns:
        User: Objeto do usuário autenticado.

    Raises:
        HTTPException: Se o token for inválido, o email não existir ou o
        usuário não for encontrado no banco, erro 401 (Unauthorized).
    """
    credentials_exception = HTTPException(
        status_code=HTTPStatus.UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )
    try:
        payload = decode(token, SECRET_KEY, algorithms=ALGORITHM)
        subject_email = payload.get('sub')
        if not subject_email:
            raise credentials_exception
    except DecodeError:
        raise credentials_exception

    user = session.scalar(select(User).where(User.email == subject_email))

    if not user:
        raise credentials_exception

    return user

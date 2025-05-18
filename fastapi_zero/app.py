from http import HTTPStatus

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from fastapi_zero.schemas import (
    Message,
    UserDB,
    UserList,
    UserPublic,
    UserSchema,
)

app = FastAPI(title='FastAPI Zero')

database = []


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
def read_users():
    """
    Retorna uma lista de usuários cadastrados.
    Esta função manipula requisições GET para a rota '/users/'.

    Returns:
        UserList: Um dicionário contendo uma lista de usuários
        cadastrados no banco de dados simulado.
    """
    return {'users': database}


@app.post('/users/', status_code=HTTPStatus.CREATED, response_model=UserPublic)
def create_user(user: UserSchema):
    """
    Cria um novo usuário e o adiciona ao banco de dados simulado.
    Esta função manipula requisições POST para a rota '/users/'.
    O usuário é criado a partir dos dados fornecidos no corpo da requisição.
    O ID do usuário é gerado automaticamente.
    O usuário criado é retornado na resposta.

    Args:
        user (UserSchema): Um objeto que contém os
        dados do usuário a ser criado.

    Returns:
        UserPublic: Um objeto que representa o usuário criado,
        sem expor a senha.
    """
    user_with_id = UserDB(**user.model_dump(), id=len(database) + 1)

    database.append(user_with_id)

    return user_with_id


@app.put('/users/{user_id}', response_model=UserPublic)
def update_user(user_id: int, user: UserSchema):
    """
    Atualiza os dados de um usuário existente no banco de dados simulado.
    Esta função manipula requisições PUT para a rota '/users/{user_id}'.
    O usuário é atualizado a partir dos dados fornecidos no
    corpo da requisição. O ID do usuário é mantido.

    Args:
        user_id (int): O ID do usuário a ser atualizado.
        user (UserSchema): Um objeto que contém os dados do usuário a ser
        atualizado.

    Returns:
        UserPublic: Um objeto que representa o usuário atualizado,
        sem expor a senha.
    """
    if user_id > len(database) or user_id < 1:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User not found'
        )

    user_with_id = UserDB(**user.model_dump(), id=user_id)
    database[user_id - 1] = user_with_id
    return user_with_id


@app.delete('/users/{user_id}', response_model=Message)
def delete_user(user_id: int):
    """
    Deleta um usuário do banco de dados simulado.
    Esta função manipula requisições DELETE para a rota '/users/{user_id}'.

    Args:
        user_id (int): O ID do usuário a ser deletado.

    Returns:
        Message: Um dicionário contendo uma mensagem de sucesso.
    """
    if user_id > len(database) or user_id < 1:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User not found'
        )

    del database[user_id - 1]

    return {'message': 'User deleted'}


@app.get('/users/{user_id}', response_model=UserPublic)
def get_user(user_id: int):
    """
    Retorna os dados de um usuário específico.
    Esta função manipula requisições GET para a rota '/users/{user_id}'.

    Args:
        user_id (int): O ID do usuário a ser retornado.

    Returns:
        UserPublic: Um objeto que representa o usuário solicitado,
        sem expor a senha.
    """
    if user_id > len(database) or user_id < 1:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User not found'
        )

    return database[user_id - 1]

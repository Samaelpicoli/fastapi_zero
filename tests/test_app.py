from http import HTTPStatus

from fastapi_zero.schemas import UserPublic


def test_root_deve_retornar_hello_world(client):
    """
    Testa se o endpoint raiz (/) retorna o status code 200
    e a mensagem 'Hello World!'.

    Verifica se a resposta da API contém o status code OK e se
    o corpo da resposta é um JSON com a chave 'message' contendo
    o valor 'Hello World!'.
    """
    response = client.get('/')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Hello World!'}


def test_hello_deve_retornar_html_com_hello_world(client):
    """
    Testa se o endpoint /hello retorna uma página HTML contendo 'Hello World!'.

    Verifica se a resposta da API contém o status code OK e
    se o corpo da resposta contém a tag HTML <h1> com o texto 'Hello World!'.
    """
    response = client.get('/hello')
    assert response.status_code == HTTPStatus.OK
    assert '<h1>Hello World!</h1>' in response.text


def test_create_user_deve_retornar_usuario_criado(client):
    """
    Testa se o endpoint /users/ cria um usuário e retorna os
    dados do usuário criado.

    Verifica se a resposta da API contém o status code 201 (Created) e
    se o corpo da resposta contém os dados do usuário criado, incluindo
    o ID gerado automaticamente.
    """
    user_data = {
        'username': 'testuser',
        'email': 'teste@teste.com',
        'password': 'testpassword',
    }
    response = client.post('/users/', json=user_data)

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'id': 1,
        'username': 'testuser',
        'email': 'teste@teste.com',
    }


def test_create_user_deve_retornar_erro_409_quando_usuario_ja_existe(
    client, user
):
    """
    Testa se o endpoint /users/ retorna erro 409 quando
    o usuário já existe.

    Verifica se a resposta da API contém o status code 409 (Conflict)
    e se o corpo da resposta contém uma mensagem de erro indicando que
    o nome de usuário já existe.
    """
    response = client.post(
        '/users/',
        json={
            'username': 'testuser',
            'email': 'test@test.com',
            'password': 'testpassword',
        },
    )
    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Username already exists'}


def test_create_user_deve_retornar_erro_409_quando_email_ja_existe(
    client, user
):
    """
    Testa se o endpoint /users/ retorna erro 409 quando
    o email já existe.

    Verifica se a resposta da API contém o status code 409 (Conflict)
    e se o corpo da resposta contém uma mensagem de erro indicando que
    o email do usuário já existe.
    """
    response = client.post(
        '/users/',
        json={
            'username': 'sama',
            'email': 'test@test.com',
            'password': 'testpassword',
        },
    )
    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Email already exists'}


def test_read_users_deve_retornar_lista_de_usuarios_vazia(client):
    """
    Testa se o endpoint /users/ retorna uma lista de usuários.

    Verifica se a resposta da API contém o status code 200 (OK).
    """
    response = client.get('/users/')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': []}


def test_read_users_deve_retornar_lista_de_usuarios_com_usuarios(client, user):
    """
    Testa se o endpoint /users/ retorna uma lista de usuários.
    Utiliza a fixture 'user' para criar um usuário no banco de dados.

    Verifica se a resposta da API contém o status code 200 (OK) e
    se o corpo da resposta contém os dados do usuário criado.
    """
    user_schema = UserPublic.model_validate(user).model_dump()
    response = client.get('/users/')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': [user_schema]}


def test_update_user_deve_retornar_usuario_atualizado(client, user):
    """
    Testa se o endpoint /users/{user_id} atualiza os dados de um usuário.
    Utiliza a fixture 'user' para criar um usuário no banco de dados.

    Verifica se a resposta da API contém o status code 200 (OK) e
    se o corpo da resposta contém os dados do usuário atualizado.
    """
    response = client.put(
        '/users/1',
        json={
            'username': 'updateduser',
            'email': 'update@update.com',
            'password': 'updatepassword',
        },
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': 1,
        'username': 'updateduser',
        'email': 'update@update.com',
    }


def test_update_user_deve_retornar_erro_404_quando_usuario_nao_existe(client):
    """
    Testa se o endpoint /users/{user_id} retorna erro 404 quando
    o usuário não existe.

    Verifica se a resposta da API contém o status code 404 (Not Found)
    e se o corpo da resposta contém uma mensagem de erro indicando que
    o usuário não foi encontrado.
    """
    response = client.put(
        '/users/999',
        json={
            'username': 'updateduser',
            'email': 'update@user.com',
            'password': 'updatepassword',
        },
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}


def test_update_user_deve_retornar_erro_409_quando_usuario_ja_existe(
    client, user
):
    """
    Testa se o endpoint /users/{user_id} retorna erro 409 quando
    o usuário já existe.

    Verifica se a resposta da API contém o status code 409 (Conflict)
    e se o corpo da resposta contém uma mensagem de erro indicando que
    o nome de usuário ou e-mail já existem.
    """
    client.post(
        '/users/',
        json={
            'username': 'sama',
            'email': 'sama@sama.com',
            'password': 'sama',
        },
    )
    response = client.put(
        '/users/1',
        json={
            'username': 'sama',
            'email': 'sama@sama.com',
            'password': 'sama',
        },
    )
    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {
        'detail': 'Username or email already exists',
    }


def test_delete_user_deve_retornar_mensagem_de_usuario_deletado(client, user):
    """
    Testa se o endpoint /users/{user_id} deleta um usuário.
    Utiliza a fixture 'user' para criar um usuário no banco de dados.

    Verifica se a resposta da API contém o status code 200 (OK) e
    se o corpo da resposta contém uma mensagem de sucesso indicando
    que o usuário foi deletado.
    """
    response = client.delete('/users/1')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'User deleted'}


def test_delete_user_deve_retornar_erro_404_quando_usuario_nao_existe(client):
    """
    Testa se o endpoint /users/{user_id} retorna erro 404 quando
    o usuário não existe.

    Verifica se a resposta da API contém o status code 404 (Not Found)
    e se o corpo da resposta contém uma mensagem de erro indicando que
    o usuário não foi encontrado.
    """
    response = client.delete('/users/999')
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}


def test_get_user_deve_retornar_usuario(client, user):
    """
    Testa se o endpoint /users/{user_id} retorna os dados de um usuário.
    Utiliza a fixture 'user' para criar um usuário no banco de dados.

    Verifica se a resposta da API contém o status code 200 (OK) e
    se o corpo da resposta contém os dados do usuário criado.
    """
    response = client.get('/users/1')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': 1,
        'username': 'testuser',
        'email': 'test@test.com',
    }


def test_get_user_deve_retornar_erro_404_quando_usuario_nao_existe(client):
    """
    Testa se o endpoint /users/{user_id} retorna erro 404 quando
    o usuário não existe.

    Verifica se a resposta da API contém o status code 404 (Not Found)
    e se o corpo da resposta contém uma mensagem de erro indicando que
    o usuário não foi encontrado.
    """
    response = client.get('/users/999')
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}

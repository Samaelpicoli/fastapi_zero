from http import HTTPStatus

from fastapi_zero.schemas import UserPublic


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
            'username': user.username,
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
            'email': user.email,
            'password': 'testpassword',
        },
    )
    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Email already exists'}


def test_read_users_deve_retornar_lista_de_usuarios(client, user, token):
    """
    Testa se o endpoint /users/ retorna uma lista de usuários.
    Utiliza a fixture 'user' para criar um usuário no banco de dados.

    Verifica se a resposta da API contém o status code 200 (OK) e
    se o corpo da resposta contém os dados do usuário criado.
    """
    user_schema = UserPublic.model_validate(user).model_dump()
    response = client.get(
        '/users/', headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': [user_schema]}


def test_update_user_deve_retornar_usuario_atualizado(client, user, token):
    """
    Testa se o endpoint /users/{user_id} atualiza os dados de um usuário
    e retorna os dados atualizados.

    Verifica se a resposta da API contém o status code 200 (OK) e
    se o corpo da resposta contém os dados do usuário atualizados,
    incluindo o novo nome de usuário e email.
    """
    response = client.put(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
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


def test_update_user_deve_retornar_erro_409_quando_usuario_ja_existe(
    client, user, other_user, token
):
    """
    Testa se o endpoint /users/{user_id} retorna erro 409 quando
    o usuário já existe.

    Verifica se a resposta da API contém o status code 409 (Conflict)
    e se o corpo da resposta contém uma mensagem de erro indicando que
    o nome de usuário ou e-mail já existem.
    """
    response = client.put(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': other_user.username,
            'email': 'sama@sama.com',
            'password': 'sama',
        },
    )
    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {
        'detail': 'Username or email already exists',
    }


def test_update_user_deve_retornar_erro_403_id_de_outro_usuario(
    client, other_user, token
):
    """
    Testa se o endpoint /users/{user_id} retorna erro 403 quando
    um usuário tenta atualizar os dados de outro usuário.

    Verifica se a resposta da API contém o status code 403 (Forbidden)
    e se o corpo da resposta contém uma mensagem de erro indicando que
    o usuário não tem permissões suficientes.
    """
    response = client.put(
        f'/users/{other_user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'sama',
            'email': 'sama@sama.com',
            'password': 'sama',
        },
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Not enough permissions'}


def test_delete_user_deve_retornar_mensagem_de_usuario_deletado(
    client, user, token
):
    """
    Testa se o endpoint /users/{user_id} retorna uma mensagem de sucesso
    quando um usuário é deletado.

    Verifica se a resposta da API contém o status code 200 (OK) e
    se o corpo da resposta contém uma mensagem indicando que o
    usuário foi deletado com sucesso.
    """
    response = client.delete(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'User deleted'}


def test_delete_user_deve_retornar_erro_403_id_de_outro_usuario(
    client, other_user, token
):
    """
    Testa se o endpoint /users/{user_id} retorna erro 403 quando
    um usuário tenta deletar outro usuário.

    Verifica se a resposta da API contém o status code 403 (Forbidden)
    e se o corpo da resposta contém uma mensagem de erro indicando que
    o usuário não tem permissões suficientes.
    """
    response = client.delete(
        f'/users/{other_user.id}',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Not enough permissions'}


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
        'username': user.username,
        'email': user.email,
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

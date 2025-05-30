from http import HTTPStatus

from fastapi_zero.security import create_access_token


def test_get_token_deve_retornar_token_de_acesso(client, user):
    """
    Testa se o endpoint /token retorna um token de acesso JWT.

    Verifica se a resposta da API contém o status code 200 (OK) e
    se o corpo da resposta contém o token de acesso JWT.
    """
    response = client.post(
        '/auth/token',
        data={
            'username': user.email,
            'password': user.clean_password,
        },
    )
    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in response.json()
    assert response.json()['token_type'] == 'Bearer'


def test_get_current_user_without_email(client):
    """
    Testa se a autenticação falha quando o token não contém o email do usuário.

    Verifica se a resposta da API contém o status code 401 (Unauthorized) e
    se o corpo da resposta contém uma mensagem de erro indicando que as
    credenciais não puderam ser validadas.
    """
    data = {'no-email': 'test'}
    token = create_access_token(data)

    response = client.delete(
        '/users/1',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}


def test_get_current_user_does_not_exists(client):
    """
    Testa se a autenticação falha quando o usuário do token não existe.

    Verifica se a resposta da API contém o status code 401 (Unauthorized) e
    se o corpo da resposta contém uma mensagem de erro indicando que as
    credenciais não puderam ser validadas.
    """
    data = {'sub': 'test@test'}
    token = create_access_token(data)
    response = client.delete(
        '/users/1',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}


def test_login_with_wrong_password(client, user):
    """
    Testa se o login falha quando a senha está incorreta.

    Verifica se a resposta da API contém o status code 401 (Unauthorized) e
    se o corpo da resposta contém uma mensagem de erro indicando que o
    email ou senha estão incorretos.
    """
    response = client.post(
        '/auth/token',
        data={'username': user.email, 'password': 'XXXXX_password'},
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Incorrect email or password'}


def test_login_with_wrong_username(client, user):
    """
    Testa se o login falha quando o nome de usuário está incorreto.

    Verifica se a resposta da API contém o status code 401 (Unauthorized) e
    se o corpo da resposta contém uma mensagem de erro indicando que o
    email ou senha estão incorretos.
    """
    response = client.post(
        '/auth/token',
        data={'username': 'XXXXXXXXXXX', 'password': user.clean_password},
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Incorrect email or password'}

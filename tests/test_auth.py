from http import HTTPStatus

from freezegun import freeze_time

from fastapi_zero.security import create_access_token


def test_token_expirou_depois_do_tempo_definido(client, user):
    """
    Testa se o token JWT expira após o tempo definido.
    Verifica se o token JWT expira corretamente após o tempo definido
    e se o endpoint /auth/token retorna um erro 401 (Unauthorized)
    quando o token expirado é usado para acessar um recurso protegido.

    O freeze_time é usado para simular o tempo de expiração do token. Ele para
    o tempo em dia e hora específicos definidos.
    """
    with freeze_time('2025-12-31 12:00:00'):
        response = client.post(
            '/auth/token',
            data={
                'username': user.email,
                'password': user.clean_password,
            },
        )
        assert response.status_code == HTTPStatus.OK
        token = response.json()['access_token']

    with freeze_time('2025-12-31 12:31:01'):
        response = client.put(
            f'/users/{user.id}',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'username': 'updateduser',
                'email': 'update@update.com',
                'password': 'updatepassword',
            },
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == {'detail': 'Could not validate credentials'}


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


def test_refresh_access_token(client, token):
    """
    Testa se o endpoint /refresh/token retorna um novo token de acesso.

    Verifica se a resposta da API contém o status code 200 (OK) e
    se o corpo da resposta contém um novo token de acesso JWT.
    """
    response = client.post(
        '/auth/refresh/token',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in response.json()
    assert response.json()['token_type'] == 'Bearer'


def test_token_expired_dont_refresh_access_token(client, user):
    """
    Testa se o endpoint /refresh/token retorna erro 401 quando o token
    está expirado.

    Verifica se a resposta da API contém o status code 401 (Unauthorized) e
    se o corpo da resposta contém uma mensagem de erro indicando que as
    credenciais não puderam ser validadas.
    """
    with freeze_time('2025-12-31 12:00:00'):
        response = client.post(
            '/auth/token',
            data={
                'username': user.email,
                'password': user.clean_password,
            },
        )
        assert response.status_code == HTTPStatus.OK
        token = response.json()['access_token']

    with freeze_time('2025-12-31 12:31:01'):
        response = client.post(
            '/auth/refresh/token',
            headers={'Authorization': f'Bearer {token}'},
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == {'detail': 'Could not validate credentials'}

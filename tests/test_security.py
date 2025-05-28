from http import HTTPStatus

from jwt import decode

from fastapi_zero.security import (
    ALGORITHM,
    SECRET_KEY,
    create_access_token,
)


def test_jwt():
    """
    Testa a criação de um token JWT.
    Esta função verifica se o token JWT é criado corretamente com os dados
    fornecidos e se o token contém as informações esperadas.
    Ela também verifica se o token inclui a data de expiração.
    """
    data = {'test': 'test'}
    token = create_access_token(data)
    decoded = decode(token, SECRET_KEY, algorithms=ALGORITHM)

    assert decoded['test'] == data['test']
    assert 'exp' in decoded


def test_jwt_invalid_token(client):
    """
    Testa a validação de um token JWT inválido.
    Esta função verifica se o servidor retorna um erro 401 (Unauthorized)
    quando um token JWT inválido é fornecido na requisição.
    """
    response = client.delete(
        '/users/1',
        headers={'Authorization': 'Bearer invalid_token'},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}

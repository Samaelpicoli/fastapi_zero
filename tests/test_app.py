from http import HTTPStatus


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

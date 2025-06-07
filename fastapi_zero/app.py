from http import HTTPStatus

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from fastapi_zero.routers import auth, users
from fastapi_zero.schemas import Message

app = FastAPI(title='FastAPI Zero')

app.include_router(auth.router)
app.include_router(users.router)


@app.get('/', status_code=HTTPStatus.OK, response_model=Message)
async def read_root():
    """
    Retorna uma mensagem de boas-vindas.
    Esta função manipula requisições GET para a rota raiz ('/').

    Returns:
        dict: Um dicionário contendo a mensagem 'Hello World!'
    """
    return {'message': 'Hello World!'}


@app.get('/hello', status_code=HTTPStatus.OK, response_class=HTMLResponse)
async def hello_world():
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

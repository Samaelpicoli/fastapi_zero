import pytest
from fastapi.testclient import TestClient

from fastapi_zero.app import app


@pytest.fixture
def client():
    """
    Cria um cliente de teste para a aplicação FastAPI.
    Uma fixture é uma função que fornece dados ou objetos para os testes.
    Neste caso, a fixture 'client' cria um cliente de teste que pode ser
    usado em diferentes testes para fazer requisições à aplicação.

    Returns:
        TestClient: Um cliente de teste configurado para a aplicação.
    """
    return TestClient(app)

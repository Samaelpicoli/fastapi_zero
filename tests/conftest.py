from contextlib import contextmanager
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from fastapi_zero.app import app
from fastapi_zero.database import get_session
from fastapi_zero.models import User, table_registry


@pytest.fixture
def client(session):
    """
    Cria um cliente de teste para a aplicação FastAPI.
    Esta função cria um cliente de teste que pode ser usado para
    fazer requisições à aplicação durante os testes. A função
    substitui a dependência de sessão do banco de dados pela
    sessão de teste fornecida. Após os testes, a dependência
    é restaurada.

    Args:
        session (Session): A sessão de banco de dados para os testes.

    Yields:
        TestClient: Um cliente de teste configurado para a aplicação.
    """

    def get_session_override():
        """
        Substitui a dependência de sessão do banco de dados pela
        sessão de teste fornecida.
        Esta função é usada para garantir que a sessão de teste
        seja usada durante os testes, em vez da sessão padrão
        definida na aplicação.

        Returns:
            Session: A sessão de banco de dados para os testes.
        """
        return session

    with TestClient(app) as test_client:
        app.dependency_overrides[get_session] = get_session_override
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def session():
    """
    Cria uma sessão de banco de dados em memória para testes.

    Esta função cria um banco de dados SQLite em memória e inicializa
    as tabelas definidas no modelo. A sessão é usada para interagir com
    o banco de dados durante os testes. Após os testes, a sessão é
    descartada e o banco de dados é limpo.

    Yields:
        Session: Uma sessão de banco de dados configurada para os testes.
    """
    engine = create_engine(
        'sqlite:///:memory:',
        connect_args={'check_same_thread': False},
        poolclass=StaticPool,
    )
    table_registry.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

    table_registry.metadata.drop_all(engine)


@pytest.fixture
def user(session: Session):
    """
    Cria um usuário de teste no banco de dados.
    Esta função cria um usuário com nome de usuário, email e senha
    fornecidos. O usuário é adicionado à sessão do banco de dados
    e a sessão é confirmada. Após a confirmação, o usuário é
    recuperado e retornado.

    Args:
        session (Session): A sessão de banco de dados para os testes.

    Returns:
        User: O usuário criado no banco de dados.
    """
    user = User(
        username='testuser', email='test@test.com', password='testpassword'
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@contextmanager
def _mock_db_time(model, time=datetime(2025, 5, 20)):
    """
    Gerencia um contexto para simular o tempo em um modelo SQLAlchemy.
    Esta função é um gerenciador de contexto que substitui o valor
    do campo 'created_at' do modelo especificado pelo valor de tempo
    fornecido. O valor padrão é 20 de maio de 2025. Após o uso, o
    gerenciador de contexto remove o evento que foi adicionado.

    Args:
        model: O modelo SQLAlchemy que contém o campo 'created_at'.
        time (datetime, opcional): O valor de tempo a ser simulado.
        O padrão é 20 de maio de 2025.

    Yields:
        datetime: O valor de tempo simulado.
    """

    def fake_time_hook(mapper, connection, target):
        """
        Função de gancho que substitui o valor do campo 'created_at'
        do modelo pelo valor de tempo fornecido.

        Args:
            mapper: O mapeador SQLAlchemy.
            connection: A conexão com o banco de dados.
            target: O objeto alvo que está sendo inserido.
        """
        if hasattr(target, 'created_at'):
            target.created_at = time
        if hasattr(target, 'updated_at'):
            target.updated_at = time

    event.listen(model, 'before_insert', fake_time_hook)

    yield time

    event.remove(model, 'before_insert', fake_time_hook)


@pytest.fixture
def mock_db_time():
    """
    Fixture que fornece um gerenciador de contexto para simular o
    tempo em um modelo SQLAlchemy. O valor padrão é 20 de maio de
    2025. Esta fixture pode ser usada em testes para garantir que
    o campo 'created_at' do modelo tenha um valor específico.

    Returns:
        _mock_db_time: O gerenciador de contexto que simula o tempo.
    """
    return _mock_db_time

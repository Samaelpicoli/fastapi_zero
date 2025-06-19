from dataclasses import asdict

import pytest
from sqlalchemy import select
from sqlalchemy.exc import DataError
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_zero.models import Todo, User


@pytest.mark.asyncio
async def test_create_user(session: AsyncSession, mock_db_time):
    """
    Testa a criação de um usuário no banco de dados.
    Verifica se o usuário é criado corretamente com os dados fornecidos
    e se o campo 'created_at' e 'updated_at' é definido corretamente.
    """
    with mock_db_time(model=User) as time:
        new_user = User(
            username='testuser',
            email='teste@teste.com',
            password='testpassword',
        )
        session.add(new_user)
        await session.commit()

        user = await session.scalar(
            select(User).where(User.username == 'testuser')
        )

    assert asdict(user) == {
        'id': 1,
        'username': 'testuser',
        'email': 'teste@teste.com',
        'password': 'testpassword',
        'created_at': time,
        'updated_at': time,
        'todos': [],
    }


@pytest.mark.asyncio
async def test_create_todo_com_state_invalido(session, user):
    """
    Testa a criação de um Todo com um estado inválido.
    Verifica se uma exceção é levantada quando o estado do Todo
    não corresponde a nenhum dos estados definidos na enumeração TodoState.
    """
    todo = Todo(
        title='Invalid State Todo',
        description='This todo has an invalid state',
        state='invalid_state',
        user_id=user.id,
    )
    session.add(todo)
    with pytest.raises(DataError):
        await session.scalar(select(Todo))

from dataclasses import asdict

from sqlalchemy import select

from fastapi_zero.models import User


def test_create_user(session, mock_db_time):
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
        session.commit()

        user = session.scalar(select(User).where(User.username == 'testuser'))

    assert asdict(user) == {
        'id': 1,
        'username': 'testuser',
        'email': 'teste@teste.com',
        'password': 'testpassword',
        'created_at': time,
        'updated_at': time,
    }

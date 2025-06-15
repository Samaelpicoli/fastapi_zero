from http import HTTPStatus

import factory
import factory.fuzzy
import pytest

from fastapi_zero.models import Todo, TodoState


class TodoFactory(factory.Factory):
    """
    Factory para criar instâncias do modelo Todo.
    Esta factory é usada para gerar objetos Todo com dados aleatórios
    para testes, facilitando a criação de múltiplos objetos com
    diferentes atributos.

    Esta factory utiliza a biblioteca `factory_boy` para gerar
    instâncias do modelo Todo com atributos aleatórios, como título,
    descrição e estado. O estado é escolhido aleatoriamente entre os
    estados definidos na enumeração TodoState. O ID do usuário é
    definido como 1 por padrão, mas pode ser alterado conforme necessário.

    Attributes:
        title (str): Título da tarefa.
        description (str): Descrição da tarefa.
        state (TodoState): Estado da tarefa, escolhido aleatoriamente
            entre os estados definidos na enumeração TodoState.
        user_id (int): ID do usuário associado à tarefa, padrão é 1.
    """

    class Meta:
        model = Todo

    title = factory.Faker('text')
    description = factory.Faker('text')
    state = factory.fuzzy.FuzzyChoice(TodoState)
    user_id = 1


def test_create_todo_deve_criar_novo_todo(client, token, mock_db_time):
    """
    Testa a criação de um novo Todo.
    Verifica se o endpoint /todos/ cria um novo Todo e retorna os
    dados do Todo criado, incluindo o ID gerado automaticamente,
    título, descrição, estado e timestamps de criação e atualização.
    """
    with mock_db_time(model=Todo) as time:
        response = client.post(
            '/todos/',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'title': 'Test Todo',
                'description': 'Test todo description',
                'state': 'todo',
            },
        )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'id': 1,
        'title': 'Test Todo',
        'description': 'Test todo description',
        'state': 'todo',
        'created_at': time.isoformat(),
        'updated_at': time.isoformat(),
    }


@pytest.mark.asyncio
async def test_list_todos_deve_retornar_5_todos(session, client, user, token):
    """
    Testa se o endpoint /todos/ retorna uma lista de 5 todos.
    Verifica se a resposta da API contém o status code 200 (OK) e
    se o corpo da resposta contém exatamente 5 tarefas (todos) criadas
    pelo usuário autenticado, verificando se o número de tarefas
    retornadas é igual ao número esperado.
    """
    expected_todos = 5
    session.add_all(TodoFactory.create_batch(expected_todos, user_id=user.id))
    await session.commit()
    response = client.get(
        '/todos/',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()['todos']) == expected_todos


@pytest.mark.asyncio
async def test_list_todos_should_retorna_todos_os_campos(
    session, client, user, token, mock_db_time
):
    """
    Testa se o endpoint /todos/ retorna todos os campos de um Todo.
    Verifica se a resposta da API contém o status code 200 (OK) e
    se o corpo da resposta contém todos os campos esperados de um Todo,
    incluindo o ID, título, descrição, estado, timestamps de criação e
    atualização, e se os valores correspondem aos dados do Todo criado.
    """
    with mock_db_time(model=Todo) as time:
        todo = TodoFactory.create(user_id=user.id)
        session.add(todo)
        await session.commit()

    await session.refresh(todo)
    response = client.get(
        '/todos/',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.json()['todos'] == [
        {
            'created_at': time.isoformat(),
            'updated_at': time.isoformat(),
            'description': todo.description,
            'id': todo.id,
            'state': todo.state,
            'title': todo.title,
        }
    ]


@pytest.mark.asyncio
async def test_list_todos_paginacao_deve_retornar_2_todos(
    session, user, client, token
):
    """
    Testa a paginação da lista de todos.
    Verifica se o endpoint /todos/ com parâmetros de paginação
    retorna exatamente 2 tarefas (todos) quando solicitado com
    offset=1 e limit=2, garantindo que a paginação funcione corretamente
    e que o número de tarefas retornadas corresponda ao limite especificado.
    """
    expected_todos = 2
    session.add_all(TodoFactory.create_batch(5, user_id=user.id))
    await session.commit()

    response = client.get(
        '/todos/?offest=1&limit=2',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()['todos']) == expected_todos


@pytest.mark.asyncio
async def test_list_todos_titulo_filtrado_deve_retornar_5_todos(
    session, user, client, token
):
    """
    Testa o filtro de título na lista de todos.
    Verifica se o endpoint /todos/ com um filtro de título retorna
    exatamente 5 tarefas (todos) que correspondem ao título especificado,
    garantindo que o filtro funcione corretamente e que o número de
    tarefas retornadas corresponda ao número esperado.
    """
    expected_todos = 5
    session.add_all(
        TodoFactory.create_batch(
            expected_todos, user_id=user.id, title='Test Todo 1'
        )
    )
    session.add_all(TodoFactory.create_batch(expected_todos, user_id=user.id))
    await session.commit()

    response = client.get(
        '/todos/?title=Test Todo',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()['todos']) == expected_todos


@pytest.mark.asyncio
async def test_list_todos_descricao_filtrado_deve_retornar_5_todos(
    session, user, client, token
):
    """
    Testa o filtro de descrição na lista de todos.
    Verifica se o endpoint /todos/ com um filtro de descrição retorna
    exatamente 5 tarefas (todos) que correspondem à descrição especificada,
    garantindo que o filtro funcione corretamente e que o número de
    tarefas retornadas corresponda ao número esperado.
    """
    expected_todos = 5
    session.add_all(
        TodoFactory.create_batch(
            expected_todos, user_id=user.id, description='description'
        )
    )
    await session.commit()

    response = client.get(
        '/todos/?description=descri',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()['todos']) == expected_todos


@pytest.mark.asyncio
async def test_list_todos_estado_filtrado_deve_retornar_5_todos(
    session, user, client, token
):
    """
    Testa o filtro de estado na lista de todos.
    Verifica se o endpoint /todos/ com um filtro de estado retorna
    exatamente 5 tarefas (todos) que correspondem ao estado especificado,
    garantindo que o filtro funcione corretamente e que o número de
    tarefas retornadas corresponda ao número esperado.
    """
    expected_todos = 5
    session.add_all(
        TodoFactory.create_batch(
            expected_todos, user_id=user.id, state=TodoState.done
        )
    )
    await session.commit()

    response = client.get(
        '/todos/?state=done',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()['todos']) == expected_todos


@pytest.mark.asyncio
async def test_list_todos_com_todos_os_filtros_combinados(
    session, user, client, token
):
    """
    Testa a combinação de filtros na lista de todos.
    Verifica se o endpoint /todos/ com múltiplos filtros (título,
    descrição e estado) retorna exatamente 5 tarefas (todos) que
    correspondem a todos os critérios especificados, garantindo que
    a combinação de filtros funcione corretamente e que o número de
    tarefas retornadas corresponda ao número esperado.
    """
    expected_todos = 5
    session.add_all(
        TodoFactory.create_batch(
            expected_todos,
            user_id=user.id,
            title='Test Todo',
            description='description',
            state=TodoState.todo,
        )
    )
    await session.commit()

    response = client.get(
        '/todos/?title=Test Todo&description=descri&state=todo',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()['todos']) == expected_todos


def test_delete_todo_deve_retornar_erro_404_se_todo_nao_existe(client, token):
    """
    Testa a exclusão de um Todo que não existe.
    Verifica se o endpoint /todos/{todo_id} retorna um erro 404 (Not Found)
    quando uma tentativa de exclusão é feita em um Todo que não existe,
    garantindo que a API trate corretamente a situação de um Todo inexistente.
    """
    response = client.delete(
        '/todos/10',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Task not found.'}


@pytest.mark.asyncio
async def test_delete_todo_deve_deletar_todo_existente(
    session, client, user, token
):
    """
    Testa a exclusão de um Todo existente.
    Verifica se o endpoint /todos/{todo_id} exclui corretamente um Todo
    existente e retorna uma mensagem de sucesso, garantindo que a
    exclusão funcione conforme esperado e que o Todo seja removido
    do banco de dados.
    """
    todo = TodoFactory(user_id=user.id)
    session.add(todo)
    await session.commit()

    response = client.delete(
        f'/todos/{todo.id}',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Task has been deleted successfully'}


@pytest.mark.asyncio
async def test_delete_todo_deve_retornar_404_se_todo_nao_pertencer_ao_usuario(
    session, client, token, other_user
):
    """
    Testa a exclusão de um Todo que pertence a outro usuário.
    Verifica se o endpoint /todos/{todo_id} retorna um erro 404 (Not Found)
    quando uma tentativa de exclusão é feita em um Todo que pertence a
    outro usuário, garantindo que a API trate corretamente a situação
    de um Todo que não pertence ao usuário autenticado.
    """
    todo_other_user = TodoFactory(user_id=other_user.id)
    session.add(todo_other_user)
    await session.commit()
    response = client.delete(
        f'/todos/{todo_other_user.id}',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Task not found.'}


def test_patch_todo_deve_retornar_404_se_todo_nao_existe(client, token):
    """
    Testa a atualização de um Todo que não existe.
    Verifica se o endpoint /todos/{todo_id} retorna um erro 404 (Not Found)
    quando uma tentativa de atualização é feita em um Todo que não existe,
    garantindo que a API trate corretamente a situação de um Todo inexistente.
    """
    response = client.patch(
        '/todos/10',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'title': 'Updated Todo',
            'description': 'Updated description',
            'state': 'done',
        },
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Task not found.'}


@pytest.mark.asyncio
async def test_patch_todo_deve_atualizar_todo_existente(
    session, client, user, token, mock_db_time
):
    """
    Testa a atualização de um Todo existente.
    Verifica se o endpoint /todos/{todo_id} atualiza corretamente um Todo
    existente e retorna os dados atualizados, incluindo o ID, título,
    descrição, estado e timestamps de criação e atualização, garantindo que
    a atualização funcione conforme esperado e que os dados retornados
    correspondam aos dados do Todo atualizado.
    """
    with mock_db_time(model=Todo) as time:
        todo = TodoFactory(user_id=user.id)
        session.add(todo)
        await session.commit()
        response = client.patch(
            f'/todos/{todo.id}',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'title': 'Updated Todo',
                'description': 'Updated description',
                'state': 'done',
            },
        )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': todo.id,
        'title': 'Updated Todo',
        'description': 'Updated description',
        'state': 'done',
        'created_at': time.isoformat(),
        'updated_at': response.json()['updated_at'],
    }

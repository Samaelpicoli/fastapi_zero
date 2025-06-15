from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_zero.database import get_session
from fastapi_zero.models import Todo, User
from fastapi_zero.schemas import (
    FilterTodo,
    Message,
    TodoList,
    TodoPublic,
    TodoSchema,
    TodoUpdate,
)
from fastapi_zero.security import get_current_user

router = APIRouter(prefix='/todos', tags=['todos'])

T_Session = Annotated[AsyncSession, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post('/', response_model=TodoPublic, status_code=HTTPStatus.CREATED)
async def create_todo(todo: TodoSchema, session: T_Session, user: CurrentUser):
    """
    Cria um novo todo para o usuário autenticado.

    Args:
        todo (TodoSchema): Um objeto TodoSchema contendo os dados do novo todo.
        session (AsyncSession): A sessão do banco de dados, obtida através
        da dependência get_session.
        user (User): O usuário autenticado, obtido através do
        dependência get_current_user.

    Returns:
        TodoPublic: O objeto TodoPublic criado, contendo os dados do novo todo.
    """
    db_todo = Todo(
        user_id=user.id,
        title=todo.title,
        description=todo.description,
        state=todo.state,
    )

    session.add(db_todo)
    await session.commit()
    await session.refresh(db_todo)

    return db_todo


@router.get('/', response_model=TodoList, status_code=HTTPStatus.OK)
async def list_todos(
    user: CurrentUser,
    session: T_Session,
    todo_filter: Annotated[FilterTodo, Query()],
):
    """
    Lista os todos do usuário autenticado com base nos filtros fornecidos.
    Os filtros incluem título, descrição, estado, limite e deslocamento para
    paginação.

    Args:
        user (User): O usuário autenticado, obtido através do
        dependência get_current_user.
        session (AsyncSession): A sessão do banco de dados, obtida através
        da dependência get_session.
        todo_filter (FilterTodo): Filtros para a lista de todos, incluindo
        título, descrição, estado, limite e deslocamento.

    Returns:
        TodoList: Um objeto TodoList contendo uma lista de objetos TodoPublic
        que correspondem aos filtros aplicados.
    """
    query = select(Todo).where(Todo.user_id == user.id)

    if todo_filter.title:
        query = query.filter(Todo.title.contains(todo_filter.title))

    if todo_filter.description:
        query = query.filter(
            Todo.description.contains(todo_filter.description)
        )

    if todo_filter.state:
        query = query.filter(Todo.state == todo_filter.state)

    todos = await session.scalars(
        query.limit(todo_filter.limit).offset(todo_filter.offset)
    )
    return {'todos': todos.all()}


@router.delete('/{todo_id}', response_model=Message)
async def delete_todo(todo_id: int, session: T_Session, user: CurrentUser):
    """
    Exclui um todo específico do usuário autenticado.

    Args:
        todo_id (int): O ID do todo a ser excluído.
        session (AsyncSession): A sessão do banco de dados, obtida através
        da dependência get_session.
        user (User): O usuário autenticado, obtido através do
        dependência get_current_user.

    Returns:
        Message: Um objeto Message contendo uma mensagem de sucesso.

    Raises:
        HTTPException: Se o todo não for encontrado, uma exceção HTTP 404
        é levantada com a mensagem 'Task not found'.
    """
    todo = await session.scalar(
        select(Todo).where(Todo.id == todo_id, Todo.user_id == user.id)
    )

    if not todo:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Task not found.',
        )

    await session.delete(todo)
    await session.commit()

    return {'message': 'Task has been deleted successfully'}


@router.patch('/{todo_id}', response_model=TodoPublic)
async def patch_todo(
    todo_id: int, session: T_Session, user: CurrentUser, todo: TodoUpdate
):
    """
    Atualiza um todo específico do usuário autenticado.

    Args:
        todo_id (int): O ID do todo a ser atualizado.
        session (AsyncSession): A sessão do banco de dados, obtida através
        da dependência get_session.
        user (User): O usuário autenticado, obtido através do
        dependência get_current_user.
        todo (TodoUpdate): Um objeto TodoUpdate contendo os campos a serem
        atualizados.

    Returns:
        TodoPublic: O objeto TodoPublic atualizado.

    Raises:
        HTTPException: Se o todo não for encontrado, uma exceção HTTP 404
        é levantada com a mensagem 'Task not found'.
    """
    db_todo = await session.scalar(
        select(Todo).where(Todo.id == todo_id, Todo.user_id == user.id)
    )

    if not db_todo:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Task not found.',
        )

    for key, value in todo.model_dump(exclude_unset=True).items():
        setattr(db_todo, key, value)

    session.add(db_todo)
    await session.commit()
    await session.refresh(db_todo)

    return db_todo

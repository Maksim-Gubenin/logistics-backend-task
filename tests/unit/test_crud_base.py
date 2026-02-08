import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models import Client
from app.schemas.client import ClientCreate
from app.services.base import CRUDBase


@pytest.mark.asyncio
async def test_crud_get_multi(db_session: AsyncSession) -> None:
    """
    Tests retrieving multiple records with a specific limit (pagination).

    Verifies that the number of returned records respects the 'limit' parameter.

    Args:
        db_session: An asynchronous SQLAlchemy session fixture.
    """
    crud: CRUDBase = CRUDBase(Client)
    res = await crud.get_multi(db_session, limit=1)
    assert len(res) <= 1


@pytest.mark.asyncio
async def test_crud_delete_not_found(db_session: AsyncSession) -> None:
    """
    Tests deleting a record that does not exist.

    Verifies that trying to delete a non-existent ID returns None.

    Args:
        db_session: An asynchronous SQLAlchemy session fixture.
    """
    crud: CRUDBase = CRUDBase(Client)
    res = await crud.delete(db_session, model_id=9999)
    assert res is None


@pytest.mark.asyncio
async def test_crud_lifecycle(db_session: AsyncSession) -> None:
    """
    Tests the full lifecycle of a record: create, get ID, and update.

    Verifies creation assigns an ID and that updates are applied correctly.

    Args:
        db_session: An asynchronous SQLAlchemy session fixture.
    """
    crud: CRUDBase = CRUDBase(Client)
    new_client_data = ClientCreate(name="New", address="Addr")
    new_client = await crud.create(db_session, new_client_data)

    await db_session.flush()

    assert new_client.id is not None

    updated = await crud.update(db_session, new_client, {"name": "Updated"})
    assert updated.name == "Updated"


@pytest.mark.asyncio
async def test_crud_get_none(db_session: AsyncSession) -> None:
    """
    Tests retrieving a single record that does not exist.

    Verifies that trying to get a non-existent ID returns None.

    Args:
        db_session: An asynchronous SQLAlchemy session fixture.
    """
    crud: CRUDBase = CRUDBase(Client)
    result = await crud.get(db_session, model_id=99999)
    assert result is None


@pytest.mark.asyncio
async def test_crud_delete_none(db_session: AsyncSession) -> None:
    """
    Tests deleting a record that does not exist (same as test_crud_delete_not_found).

    Verifies that trying to delete a non-existent ID returns None.

    Args:
        db_session: An asynchronous SQLAlchemy session fixture.
    """
    crud: CRUDBase = CRUDBase(Client)
    result = await crud.delete(db_session, model_id=99999)
    assert result is None

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models import Client
from app.schemas.client import ClientCreate
from app.services.base import CRUDBase


@pytest.mark.asyncio
async def test_crud_get_multi(db_session: AsyncSession) -> None:
    crud: CRUDBase = CRUDBase(Client)
    res = await crud.get_multi(db_session, limit=1)
    assert len(res) <= 1


@pytest.mark.asyncio
async def test_crud_delete_not_found(db_session: AsyncSession) -> None:
    crud: CRUDBase = CRUDBase(Client)
    res = await crud.delete(db_session, model_id=9999)
    assert res is None


@pytest.mark.asyncio
async def test_crud_lifecycle(db_session: AsyncSession) -> None:
    crud: CRUDBase = CRUDBase(Client)
    new_client_data = ClientCreate(name="New", address="Addr")
    new_client = await crud.create(db_session, new_client_data)

    await db_session.flush()

    assert new_client.id is not None

    updated = await crud.update(db_session, new_client, {"name": "Updated"})
    assert updated.name == "Updated"


@pytest.mark.asyncio
async def test_crud_get_none(db_session: AsyncSession) -> None:
    crud: CRUDBase = CRUDBase(Client)
    result = await crud.get(db_session, model_id=99999)
    assert result is None


@pytest.mark.asyncio
async def test_crud_delete_none(db_session: AsyncSession) -> None:
    crud: CRUDBase = CRUDBase(Client)
    result = await crud.delete(db_session, model_id=99999)
    assert result is None

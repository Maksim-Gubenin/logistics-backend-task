import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    InsufficientStockError,
    NomenclatureNotFoundError,
    OrderNotFoundError,
)
from app.schemas.order import OrderCreate
from app.schemas.order_item import OrderItemCreateInput
from app.services.order_servise import order_service


@pytest.mark.asyncio
async def test_service_add_item_logic(db_session: AsyncSession) -> None:
    """
    Test case for the core business logic of adding an item to an order.

    Verifies that the `add_item_to_order` service method correctly updates the
    quantity of an existing order item within a transaction.

    Args:
        db_session: An asynchronous SQLAlchemy session fixture (pre-populated with seed data).
    """
    item_data = OrderItemCreateInput(order_id=1, nomenclature_id=1, quantity=2)
    item = await order_service.add_item_to_order(db_session, item_data)
    assert item.quantity >= 2


@pytest.mark.asyncio
async def test_order_service_exceptions(db_session: AsyncSession) -> None:
    """
    Tests that the order service correctly raises specific business logic exceptions.

    Verifies expected behavior for OrderNotFoundError, NomenclatureNotFoundError,
    and InsufficientStockError scenarios.

    Args:
        db_session: An asynchronous SQLAlchemy session fixture (pre-populated with seed data).
    """
    with pytest.raises(OrderNotFoundError):
        await order_service.add_item_to_order(
            db_session,
            OrderItemCreateInput(order_id=999, nomenclature_id=1, quantity=1)
        )
    with pytest.raises(NomenclatureNotFoundError):
        await order_service.add_item_to_order(
            db_session,
            OrderItemCreateInput(order_id=1, nomenclature_id=999, quantity=1)
        )
    with pytest.raises(InsufficientStockError):
        await order_service.add_item_to_order(
            db_session,
            OrderItemCreateInput(order_id=1, nomenclature_id=1, quantity=100)
        )


@pytest.mark.asyncio
async def test_create_full_order_success(db_session: AsyncSession) -> None:
    """
    Tests the successful creation of a complete order via the service layer.

    Verifies that a new order is created with the correct items and quantity,
    and that IDs are generated correctly after flushing the session.

    Args:
        db_session: An asynchronous SQLAlchemy session fixture (pre-populated with seed data).
    """
    order_in = OrderCreate(
        client_id=1,
        items=[
            OrderItemCreateInput(
                order_id=1,
                nomenclature_id=1,
                quantity=1
            )
        ]
    )
    order = await order_service.create_full_order(db_session, order_in)
    await db_session.flush()

    assert order.id is not None
    assert len(order.items) == 1
    assert order.items[0].quantity == 1

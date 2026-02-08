from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import db_helper
from app.core.models import OrderItem
from app.schemas.order_item import OrderItemCreateInput, OrderItemInDB
from app.services import order_service

router = APIRouter()


@router.post(
    "/add-item",
    response_model=OrderItemInDB,
    status_code=status.HTTP_201_CREATED,
    summary="Добавить или обновить позицию в существующем заказе",
    description="""
    Обрабатывает запрос на добавление товара в заказ.
    Реализует бизнес-логику:\n
    * Если товар уже есть в заказе, количество увеличивается (upsert).\n
    * Проверяет наличие товара на складе перед добавлением.\n
    * Фиксирует цену товара на момент добавления.\n
    * Использует транзакционную блокировку (`SELECT FOR UPDATE`) для предотвращения состояний гонки (race conditions).
    """,
    responses={
            status.HTTP_400_BAD_REQUEST: {"description": "Недостаточное количество товара на складе."},
            status.HTTP_404_NOT_FOUND: {"description": "Заказ не найден."},
            status.HTTP_200_OK: {"description": "Позиция заказа успешно обновлена (quantity увеличено)."}
        },
)
async def add_item_to_order_endpoint(
    item_data: OrderItemCreateInput,
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)]
) -> OrderItem:
    """
    Handles the request to add or update an item within an order.

    This endpoint orchestrates the addition or quantity update of a specific nomenclature item
    in a customer's order, ensuring data integrity through atomic operations.

    Args:
        item_data: The input data containing order ID, nomenclature ID, and quantity.
        session: The asynchronous database session dependency.

    Returns:
        The updated or newly created OrderItem database object.

    Raises:
        HTTPException: If the order is not found (404), or if there is
                       insufficient stock quantity (400).
    """
    item = await order_service.add_item_to_order(session=session, item_data=item_data)
    await session.commit()
    await session.refresh(item)
    return item

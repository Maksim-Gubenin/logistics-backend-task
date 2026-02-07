from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models.nomenclature import Nomenclature
from app.core.models.order import Order
from app.core.models.order_items import OrderItem
from app.schemas.order import OrderCreate
from app.schemas.order_item import OrderItemCreateInput, OrderItemInDB
from app.services.base import CRUDBase

crud_order: CRUDBase = CRUDBase(Order)
crud_order_item: CRUDBase = CRUDBase(OrderItem)


class OrderService:

    async def create_full_order(self, db: AsyncSession, order_in: OrderCreate) -> Order:
        nomenclature_ids = [item.nomenclature_id for item in order_in.items]

        stmt = select(Nomenclature).where(Nomenclature.id.in_(nomenclature_ids)).with_for_update()
        result = await db.execute(stmt)
        nomenclatures = result.scalars().all()

        nomenclature_map = {item.id: item for item in nomenclatures}
        for item_in in order_in.items:
            item_db = nomenclature_map.get(item_in.nomenclature_id)
            if not item_db or item_db.quantity < item_in.quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Недостаточное количество товара ID {item_in.nomenclature_id} на складе."
                )

        order_db = await crud_order.create(db, order_in)

        for item_in in order_in.items:
            nomenclature_map[item_in.nomenclature_id].quantity -= item_in.quantity
            db.add(nomenclature_map[item_in.nomenclature_id])

            price_at_purchase_decimal: Decimal = nomenclature_map[item_in.nomenclature_id].price

            order_item_create = OrderItemInDB(
                order_id=order_db.id,
                nomenclature_id=item_in.nomenclature_id,
                quantity=item_in.quantity,
                price_at_purchase=price_at_purchase_decimal
            )
            await crud_order_item.create(db, order_item_create)

        await db.refresh(order_db, attribute_names=["items"])
        return order_db

    async def add_item_to_order(
            self,
            session: AsyncSession,
            item_data: OrderItemCreateInput
    ) -> OrderItem:
        order = await session.get(Order, item_data.order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Заказ не найден")
        stmt_nom = select(Nomenclature).where(Nomenclature.id == item_data.nomenclature_id).with_for_update()
        res_nom = await session.execute(stmt_nom)
        product = res_nom.scalar_one_or_none()

        if not product or product.quantity < item_data.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Товара нет в наличии или недостаточно на складе"
            )

        stmt_item = select(OrderItem).where(
            OrderItem.order_id == item_data.order_id,
            OrderItem.nomenclature_id == item_data.nomenclature_id
        ).with_for_update()
        res_item = await session.execute(stmt_item)
        existing_item = res_item.scalar_one_or_none()

        if existing_item:
            existing_item.quantity += item_data.quantity
            order_item = existing_item
        else:
            order_item = OrderItem(
                order_id=item_data.order_id,
                nomenclature_id=item_data.nomenclature_id,
                quantity=item_data.quantity,
                price_at_purchase=product.price
            )
            session.add(order_item)

        product.quantity -= item_data.quantity

        return order_item


order_service = OrderService()

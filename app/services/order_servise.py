import logging
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import InsufficientStockError, NomenclatureNotFoundError, OrderNotFoundError
from app.core.models.nomenclature import Nomenclature
from app.core.models.order import Order
from app.core.models.order_items import OrderItem
from app.schemas.order import OrderCreate
from app.schemas.order_item import OrderItemCreateInput, OrderItemInDB
from app.services.base import CRUDBase

crud_order: CRUDBase = CRUDBase(Order)
crud_order_item: CRUDBase = CRUDBase(OrderItem)

logger = logging.getLogger(__name__)


class OrderService:
    """
    Service class encapsulating business logic for handling customer orders.

    This includes creating full orders and adding individual items, managing
    stock levels, and ensuring data consistency.
    """
    async def create_full_order(self, db: AsyncSession, order_in: OrderCreate) -> Order:
        """
        Creates a complete order with multiple items from a Pydantic schema.

        This method handles stock validation, price capture at purchase time,
        stock deduction, and atomic transaction management.

        Args:
            db: The asynchronous database session.
            order_in: The schema containing client ID and list of items to order.

        Returns:
            The fully populated Order model instance, refreshed with its items relationship.

        Raises:
            NomenclatureNotFoundError: If any item in the order list does not exist.
            InsufficientStockError: If there is not enough stock for any item requested.
        """
        nomenclature_ids = [item.nomenclature_id for item in order_in.items]

        stmt = select(Nomenclature).where(Nomenclature.id.in_(nomenclature_ids)).with_for_update()
        result = await db.execute(stmt)
        nomenclatures = result.scalars().all()

        nomenclature_map = {item.id: item for item in nomenclatures}
        for item_in in order_in.items:
            item_db = nomenclature_map.get(item_in.nomenclature_id)
            if not item_db:
                logger.warning(f"Номенклатура ID {item_in.nomenclature_id} не найдена при создании заказа.")
                raise NomenclatureNotFoundError(nomenclature_id=item_in.nomenclature_id)
            if item_db.quantity < item_in.quantity:
                logger.warning(
                    f"Недостаточно товара ID {item_in.nomenclature_id}. "
                    f"Запрошено: {item_in.quantity}, "
                    f"в наличии: {item_db.quantity}")
                raise InsufficientStockError(
                    nomenclature_id=item_in.nomenclature_id,
                    available_quantity=item_db.quantity,
                    requested_quantity=item_in.quantity
                )

        order_data = order_in.model_dump(exclude={"items"})
        order_db = Order(**order_data)
        db.add(order_db)
        await db.flush()

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
        """
        Adds a single nomenclature item to an existing order or updates quantity if present.

        Ensures atomic updates using database locking (`with_for_update()`) to prevent
        race conditions when checking/updating stock and order items.

        Args:
            session: The asynchronous database session.
            item_data: The input data (order ID, nomenclature ID, quantity).

        Returns:
            The created or updated OrderItem instance.

        Raises:
            OrderNotFoundError: If the specified order ID does not exist.
            NomenclatureNotFoundError: If the specified nomenclature ID does not exist.
            InsufficientStockError: If there is insufficient stock to fulfill the request.
        """
        order = await session.get(Order, item_data.order_id)
        if not order:
            logger.warning(f"Попытка добавить товар в несуществующий заказ ID {item_data.order_id}.")
            raise OrderNotFoundError(order_id=item_data.order_id)

        stmt_nom = select(Nomenclature).where(Nomenclature.id == item_data.nomenclature_id).with_for_update()
        res_nom = await session.execute(stmt_nom)
        product = res_nom.scalar_one_or_none()

        if not product:
            logger.warning(f"Номенклатура ID {item_data.nomenclature_id} не найдена.")
            raise NomenclatureNotFoundError(nomenclature_id=item_data.nomenclature_id)

        if product.quantity < item_data.quantity:
            logger.warning(
                f"Недостаточно товара ID {item_data.nomenclature_id}. "
                f"Запрошено: {item_data.quantity}, "
                f"в наличии: {product.quantity}")
            raise InsufficientStockError(
                nomenclature_id=item_data.nomenclature_id,
                available_quantity=product.quantity,
                requested_quantity=item_data.quantity
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

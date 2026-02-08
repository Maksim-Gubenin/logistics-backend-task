import asyncio
from contextlib import asynccontextmanager
from decimal import Decimal
from typing import AsyncGenerator

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db_hepler import db_helper
from app.core.models import Category, Client, Nomenclature, Order, OrderItem


@asynccontextmanager
async def get_session_for_script() -> AsyncGenerator[AsyncSession, None]:
    """
    Provides an asynchronous database session as a context manager for script usage.

    Yields:
        AsyncSession: The database session object.
    """
    session_generator = db_helper.session_getter()
    try:
        session = await anext(session_generator)
        yield session
    finally:
        await session_generator.aclose()


async def seed_database(session: AsyncSession) -> None:
    """
    Populates the database with initial dummy data for testing purposes.

    Creates clients, a hierarchical category tree, nomenclature items with stock,
    and a few sample orders.

    Args:
        session: The active asynchronous database session.
    """
    print("Начало наполнения БД...")

    c1 = Client(name="ИП Иванов", address="Москва")
    c2 = Client(name="ООО Ромашка", address="Питер")
    session.add_all([c1, c2])
    await session.flush()

    cat_tech = Category(name="Бытовая техника")
    cat_comp = Category(name="Компьютеры")
    session.add_all([cat_tech, cat_comp])
    await session.flush()

    cat_wash = Category(name="Стиральные машины", parent_id=cat_tech.id)
    cat_ref = Category(name="Холодильники", parent_id=cat_tech.id)
    cat_tv = Category(name="Телевизоры", parent_id=cat_tech.id)
    cat_note = Category(name="Ноутбуки", parent_id=cat_comp.id)
    session.add_all([cat_wash, cat_ref, cat_tv, cat_note])
    await session.flush()

    cat_ref_1d = Category(name="однокамерные", parent_id=cat_ref.id)
    cat_ref_2d = Category(name="двухкамерные", parent_id=cat_ref.id)
    cat_note_17 = Category(name="17 дюймов", parent_id=cat_note.id)
    cat_note_19 = Category(name="19 дюймов", parent_id=cat_note.id)
    session.add_all([cat_ref_1d, cat_ref_2d, cat_note_17, cat_note_19])
    await session.flush()

    n1 = Nomenclature(name="Bosch Serie 6", quantity=Decimal("10.00"), price=Decimal("60000.00"),
                      category_id=cat_wash.id)
    n2 = Nomenclature(name="LG Однокамерный", quantity=Decimal("5.00"), price=Decimal("45000.00"),
                      category_id=cat_ref_1d.id)
    n3 = Nomenclature(name="LG Двухкамерный", quantity=Decimal("2.00"), price=Decimal("150000.00"),
                      category_id=cat_ref_2d.id)
    n4 = Nomenclature(name="Dell XPS 17", quantity=Decimal("8.00"), price=Decimal("210000.00"),
                      category_id=cat_note_17.id)

    n_top = Nomenclature(name="Кабель питания", quantity=Decimal("1000.00"), price=Decimal("500.00"),
                         category_id=cat_tech.id)

    session.add_all([n1, n2, n3, n4, n_top])
    await session.flush()

    o1 = Order(client_id=c1.id)
    session.add(o1)
    await session.flush()
    session.add(OrderItem(order_id=o1.id, nomenclature_id=n1.id, quantity=1, price_at_purchase=n1.price))
    session.add(OrderItem(order_id=o1.id, nomenclature_id=n_top.id, quantity=10, price_at_purchase=n_top.price))

    o2 = Order(client_id=c2.id)
    session.add(o2)
    await session.flush()
    session.add(OrderItem(order_id=o2.id, nomenclature_id=n_top.id, quantity=50, price_at_purchase=n_top.price))

    await session.commit()
    print("БД наполнена.")


async def main() -> None:
    """
    Main entry point for the database seeding script.

    Checks if the database is already populated before calling the seed_database function.
    """
    async with get_session_for_script() as session:
        count_stmt = select(func.count(Client.id))
        count = await session.scalar(count_stmt)

        if count and count > 0:
            print("Внимание: БД уже содержит клиентов. Процесс наполнения пропущен.")
        else:
            await seed_database(session)


if __name__ == "__main__":
    # Executes the main function if the script is run directly.
    asyncio.run(main())

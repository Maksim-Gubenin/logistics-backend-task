from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.models.base import Base

if TYPE_CHECKING:
    from app.core.models import Nomenclature, Order


class OrderItem(Base):
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), nullable=False)
    nomenclature_id: Mapped[int] = mapped_column(ForeignKey("nomenclatures.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    price_at_purchase: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    order: Mapped["Order"] = relationship(back_populates="items")
    nomenclature: Mapped["Nomenclature"] = relationship()

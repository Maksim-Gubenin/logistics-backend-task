from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.models.base import Base

if TYPE_CHECKING:
    from app.core.models import Nomenclature, Order


class OrderItem(Base):
    """
    Represents a specific item line within a customer's order.

    This junction table records which nomenclature item was purchased, in what
    quantity, and critically, at what price at the time of the transaction
    (price_at_purchase) to ensure historical data accuracy.

    Attributes:
        order_id: Foreign key to the parent order ID.
        nomenclature_id: Foreign key to the specific product/nomenclature item ID.
        quantity: The quantity of this item purchased in the order.
        price_at_purchase: The price of the item at the exact moment the order was placed.
        order: Relationship to the parent Order object.
        nomenclature: Relationship to the Nomenclature item details.
    """
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), nullable=False)
    nomenclature_id: Mapped[int] = mapped_column(ForeignKey("nomenclatures.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    price_at_purchase: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    order: Mapped["Order"] = relationship(back_populates="items")
    nomenclature: Mapped["Nomenclature"] = relationship()

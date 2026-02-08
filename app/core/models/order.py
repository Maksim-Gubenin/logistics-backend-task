from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.models.base import Base

if TYPE_CHECKING:
    from app.core.models import Client, OrderItem


class Order(Base):
    """
    Represents a customer sales order.

    This model links a client to a collection of items they have purchased,
    recording the time of the transaction.

    Attributes:
        client_id: Foreign key to the client who placed the order.
        order_date: The date and time the order was created, defaults to now.
        client: Relationship to the Client object who owns this order.
        items: A list of OrderItem objects associated with this order (cascade deletes orphans).
    """
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"), nullable=False)
    order_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    client: Mapped["Client"] = relationship(back_populates="orders")
    items: Mapped[List["OrderItem"]] = relationship(back_populates="order", cascade="all, delete-orphan")

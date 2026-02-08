from typing import TYPE_CHECKING, List

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.models.base import Base

if TYPE_CHECKING:
    from app.core.models import Order



class Client(Base):
    """
    Represents a customer in the system.

    Stores core customer information and links to all orders placed by this client.

    Attributes:
        name: The full name or company name of the client.
        address: The primary billing/shipping address of the client.
        orders: A list of orders associated with this client.
    """
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    address: Mapped[str] = mapped_column(String(500))

    orders: Mapped[List["Order"]] = relationship(back_populates="client")

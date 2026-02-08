from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.models.base import Base

if TYPE_CHECKING:
    from app.core.models import Category


class Nomenclature(Base):
    """
    Represents a specific product or item available for sale.

    This model stores details about individual products, including stock levels
    and current pricing, linked to a specific category.

    Attributes:
        name: The name or description of the product.
        quantity: The current quantity of the item available in stock.
        price: The current selling price of the item (stored with fixed precision).
        category_id: Foreign key to the category this item belongs to.
        category: Relationship to the parent Category object.
    """
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=0)
    price: Mapped[Decimal] = mapped_column(Numeric(precision=10, scale=2), nullable=False)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=False)

    category: Mapped["Category"] = relationship(back_populates="nomenclatures")

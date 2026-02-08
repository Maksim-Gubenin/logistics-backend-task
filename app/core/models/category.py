from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.models import Base

if TYPE_CHECKING:
    from app.core.models import Nomenclature


class Category(Base):
    """
    Represents a category in the nomenclature hierarchy.

    Categories are structured in an adjacency list model to support unlimited
    levels of nesting (e.g., Electronics -> TVs -> OLED TVs).

    Attributes:
        name: The name of the category.
        parent_id: Foreign key to the parent category's ID. Null for root categories.
        parent: Relationship to the parent Category object.
        children: Relationship to a list of child Category objects.
        nomenclatures: Relationship to a list of Nomenclature items belonging to this category.
    """
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    parent_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("categories.id", ondelete="CASCADE"),
        nullable=True
    )

    parent: Mapped[Optional["Category"]] = relationship(
        remote_side="Category.id",
        back_populates="children"
    )
    children: Mapped[List["Category"]] = relationship(back_populates="parent")
    nomenclatures: Mapped[List["Nomenclature"]] = relationship(back_populates="category")

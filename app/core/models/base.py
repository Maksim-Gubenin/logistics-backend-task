"""
Base SQLAlchemy declarative base class with automatic table naming.

This module provides a custom base class for SQLAlchemy models that automatically
generates table names from class names using camelCase to snake_case conversion,
and includes a standard primary key field.
"""
import inflection
from sqlalchemy import BigInteger, MetaData
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    declared_attr,
    mapped_column,
)

from app.core.config import settings
from app.utils import camel_case_to_snake_case


class Base(DeclarativeBase):
    """
    Custom SQLAlchemy declarative base class with automatic table naming and conventions.

    This class extends SQLAlchemy's DeclarativeBase to provide:
    1.  Automatic table name generation from PascalCase class names to snake_case plural form.
    2.  A standard, automatically included primary key field (`id`).
    3.  Consistent naming conventions for constraints and indexes via `MetaData`.

    Attributes:
        id (Mapped[int]): The primary key field (BigInteger) automatically added to all models.
    """

    __abstract__ = True

    metadata = MetaData(
        naming_convention=settings.db.naming_convention,
    )

    @declared_attr.directive
    def __tablename__(cls) -> str:
        """
        Automatically generates the table name from the class name.

        Converts the PascalCase class name to snake_case and pluralizes it.

        Args:
            cls: The model class being defined.

        Returns:
            str: The table name in snake_case plural form (e.g., 'users', 'product_items').
        """
        singular_name = camel_case_to_snake_case(cls.__name__)
        return inflection.pluralize(singular_name)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

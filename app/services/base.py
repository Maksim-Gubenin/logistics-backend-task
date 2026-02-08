from typing import Any, Dict, Generic, Optional, Sequence, Type, TypeVar, Union

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)
CRUDBaseType = TypeVar("CRUDBaseType", bound="CRUDBase")

class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Generic base class for CRUD operations on SQLAlchemy models using Pydantic schemas.

    Provides core functionality for retrieving, creating, updating, and deleting
    database records asynchronously.

    Args:
        model: The SQLAlchemy model class this CRUD class operates on.
    """
    def __init__(self, model: Type[ModelType]):
        """
        Initializes the CRUDBase instance with the specific model type.
        """
        self.model: Type[ModelType] = model

    async def get(self, db: AsyncSession, model_id: int) -> ModelType | None:
        """
        Retrieves a single record by its primary key ID.

        Args:
            db: The asynchronous database session.
            model_id: The primary key ID of the record to retrieve.

        Returns:
            The model instance if found, otherwise None.
        """
        stmt = select(self.model).where(self.model.id == model_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_multi(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> Sequence[ModelType]:
        """
        Retrieves multiple records with pagination.

        Args:
            db: The asynchronous database session.
            skip: The number of records to skip (offset).
            limit: The maximum number of records to return.

        Returns:
            A sequence (list) of model instances.
        """
        stmt = select(self.model).offset(skip).limit(limit)
        result = await db.execute(stmt)
        return result.scalars().all()

    async def create(self, db: AsyncSession, obj_in: CreateSchemaType) -> ModelType:
        """
        Creates a new record from a Pydantic create schema.

        Args:
            db: The asynchronous database session.
            obj_in: The Pydantic schema containing data for the new record.

        Returns:
            The newly created and added model instance (not yet committed).
        """
        obj_in_data = obj_in.model_dump()
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        return db_obj

    async def update(
            self,
            db: AsyncSession,
            db_obj: ModelType,
            obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """
        Updates an existing database record with data from a Pydantic schema or dictionary.

        Args:
            db: The asynchronous database session.
            db_obj: The existing model instance to update.
            obj_in: The Pydantic schema (with `exclude_unset=True`) or dict of data to apply.

        Returns:
            The updated model instance (not yet committed).
        """
        if isinstance(obj_in, BaseModel):
            update_data = obj_in.model_dump(exclude_unset=True)
        else:
            update_data = obj_in

        for field in update_data:
            if hasattr(db_obj, field):
                setattr(db_obj, field, update_data[field])

        db.add(db_obj)
        return db_obj

    async def delete(self, db: AsyncSession, model_id: int) -> Optional[ModelType]:
        """
        Deletes a record by its primary key ID.

        Args:
            db: The asynchronous database session.
            model_id: The primary key ID of the record to delete.

        Returns:
            The deleted model instance if found and deleted, otherwise None.
        """
        stmt = select(self.model).where(self.model.id == model_id)
        result = await db.execute(stmt)
        db_obj = result.scalar_one_or_none()

        if db_obj:
            await db.delete(db_obj)
            return db_obj
        return None

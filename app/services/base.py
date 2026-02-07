# app/services/base.py
from typing import Any, Dict, Generic, Optional, Sequence, Type, TypeVar, Union

from pydantic import BaseModel
from sqlalchemy import select  # Добавляем delete и update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)
CRUDBaseType = TypeVar("CRUDBaseType", bound="CRUDBase")

class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self.model: Type[ModelType] = model

    async def get(self, db: AsyncSession, model_id: int) -> ModelType | None:
        stmt = select(self.model).where(self.model.id == model_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_multi(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> Sequence[ModelType]:
        stmt = select(self.model).offset(skip).limit(limit)
        result = await db.execute(stmt)
        return result.scalars().all()

    async def create(self, db: AsyncSession, obj_in: CreateSchemaType) -> ModelType:
        obj_in_data = obj_in.model_dump()
        db_obj = self.model(**obj_in_data)

        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
            self,
            db: AsyncSession,
            db_obj: ModelType,
            obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        if isinstance(obj_in, BaseModel):
            update_data = obj_in.model_dump(exclude_unset=True)
        else:
            update_data = obj_in

        for field in update_data:
            if hasattr(db_obj, field):
                setattr(db_obj, field, update_data[field])

        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def delete(self, db: AsyncSession, model_id: int) -> Optional[ModelType]:
        stmt = select(self.model).where(self.model.id == model_id)
        result = await db.execute(stmt)
        db_obj = result.scalar_one_or_none()

        if db_obj:
            await db.delete(db_obj)
            await db.commit()
            return db_obj
        return None

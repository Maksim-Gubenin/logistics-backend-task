from datetime import datetime
from typing import List

from pydantic import BaseModel, ConfigDict, PositiveInt

from app.schemas.order_item import OrderItemCreateInput, OrderItemInDB


class OrderCreate(BaseModel):
    client_id: PositiveInt
    items: List[OrderItemCreateInput]


class OrderRead(BaseModel):
    id: PositiveInt
    client_id: PositiveInt
    order_date: datetime
    items: List[OrderItemInDB]

    model_config = ConfigDict(from_attributes=True)

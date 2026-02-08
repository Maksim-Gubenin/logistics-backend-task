from datetime import datetime
from typing import List

from pydantic import BaseModel, ConfigDict, PositiveInt

from app.schemas.order_item import OrderItemCreateInput, OrderItemInDB


class OrderCreate(BaseModel):
    """
    Schema for creating a new order input data.

    Used for validating data when a client submits a new order request.

    Attributes:
        client_id: The ID of the client placing the order. Must be a positive integer.
        items: A list of items to be included in the order, with nomenclature ID and quantity.
    """
    client_id: PositiveInt
    items: List[OrderItemCreateInput]


class OrderRead(BaseModel):
    """
    Schema for representing an order retrieved from the database.

    Includes all order details, including the generated ID and precise order date/time.

    Attributes:
        id: The unique identifier for the order.
        client_id: The ID of the client who placed the order.
        order_date: The timestamp when the order was created.
        items: A list of the order items, including prices at the time of purchase.
    """
    id: PositiveInt
    client_id: PositiveInt
    order_date: datetime
    items: List[OrderItemInDB]

    model_config = ConfigDict(from_attributes=True)

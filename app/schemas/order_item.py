from decimal import Decimal

from pydantic import BaseModel, Field, PositiveInt, ConfigDict


class OrderItemCreateInput(BaseModel):
    order_id: PositiveInt
    nomenclature_id: PositiveInt
    quantity: PositiveInt


class OrderItemInDB(BaseModel):

    order_id: PositiveInt
    nomenclature_id: PositiveInt
    quantity: PositiveInt
    price_at_purchase: Decimal = Field(..., decimal_places=2)

    model_config = ConfigDict(from_attributes=True)

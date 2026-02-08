from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, PositiveInt


class OrderItemCreateInput(BaseModel):
    """
    Input schema for adding a new item to an order via API endpoint.

    Used for validating incoming request data for the 'add-item' service.
    Note: order_id might be implicit in some service implementations, but defined here
    as per the provided structure.

    Attributes:
        order_id: The ID of the target order. Must be a positive integer.
        nomenclature_id: The ID of the product being added. Must be a positive integer.
        quantity: The quantity of the product to add. Must be a positive integer.
    """
    order_id: PositiveInt
    nomenclature_id: PositiveInt
    quantity: PositiveInt


class OrderItemInDB(BaseModel):
    """
    Schema for representing an order item retrieved from the database.

    Includes the fixed price at the moment of purchase for historical accuracy.

    Attributes:
        order_id: The ID of the parent order.
        nomenclature_id: The ID of the associated product.
        quantity: The quantity purchased.
        price_at_purchase: The price of the item at the time the order was placed,
                           with 2 decimal places precision.
    """
    order_id: PositiveInt
    nomenclature_id: PositiveInt
    quantity: PositiveInt
    price_at_purchase: Decimal = Field(
        ...,
        decimal_places=2,
        examples=["60000.00"]
    )

    model_config = ConfigDict(from_attributes=True)

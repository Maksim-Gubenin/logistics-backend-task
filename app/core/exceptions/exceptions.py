class InsufficientStockError(Exception):
    """
    Exception raised for insufficient stock quantity for a specific nomenclature item.

    Attributes:
        nomenclature_id: Identifier of the nomenclature item.
        available_quantity: Quantity available in stock.
        requested_quantity: Quantity requested by the user/order.
    """
    def __init__(self, nomenclature_id: int, available_quantity: int, requested_quantity: int):
        """
        Initializes the InsufficientStockError with specific details.

        Args:
            nomenclature_id: Identifier of the nomenclature item.
            available_quantity: Quantity available in stock.
            requested_quantity: Quantity requested by the user/order.
        """
        self.nomenclature_id = nomenclature_id
        self.available_quantity = available_quantity
        self.requested_quantity = requested_quantity
        super().__init__(
            f"Недостаточное количество товара ID {nomenclature_id}. "
            f"Запрошено: {requested_quantity}, "
            f"в наличии: {available_quantity}."
        )

class OrderNotFoundError(Exception):
    """
    Exception raised when a specific order ID is not found in the database.

    Attributes:
        order_id: The identifier of the missing order.
    """
    def __init__(self, order_id: int):
        """
        Initializes the OrderNotFoundError.

        Args:
            order_id: The identifier of the missing order.
        """
        self.order_id = order_id
        super().__init__(f"Заказ с ID {order_id} не найден.")

class NomenclatureNotFoundError(Exception):
    """
    Exception raised when a specific nomenclature (product) ID is not found.

    Attributes:
        nomenclature_id: The identifier of the missing nomenclature item.
    """
    def __init__(self, nomenclature_id: int):
        """
        Initializes the NomenclatureNotFoundError.

        Args:
            nomenclature_id: The identifier of the missing nomenclature item.
        """
        self.nomenclature_id = nomenclature_id
        super().__init__(f"Номенклатура с ID {nomenclature_id} не найдена.")
